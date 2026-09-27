"""
PDF Topic Extraction + Question Generation (v2 - noun-phrase based)
---------------------------------------------------------------------
Fixes the "generic word" problem (topics like 'example', 'text') by
extracting real noun phrases/technical terms with spaCy, then ranking
them by importance with TF-IDF (or KeyBERT embeddings if available).

Questions are generated with a template engine tuned to how topic
phrases usually look in academic notes:
  - short acronym/technical term (e.g. "CNN")      -> "Explain in detail about CNN."
  - definable concept (e.g. "tokenization")        -> "What is tokenization? Explain with an example."
  - process/technique (e.g. "gradient descent")     -> "Explain how gradient descent works."
  - comparison-flavoured pair ("stemming vs lemmatization") -> comparison question

Usage:
    python topic_qgen.py path/to/file.pdf --num_topics 8 --questions_per_topic 2
"""

import argparse
import re
import sys
from collections import Counter

import pdfplumber
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

nlp = spacy.load("en_core_web_sm")

# ---------- 1. PDF TEXT EXTRACTION (with header/footer cleanup) ----------

def extract_text_from_pdf(pdf_path: str) -> str:
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t)

    # Remove lines that repeat on almost every page (headers/footers/logos/institute names)
    line_counts = Counter()
    per_page_lines = [p.split("\n") for p in pages_text]
    for lines in per_page_lines:
        for line in set(l.strip() for l in lines if l.strip()):
            line_counts[line] += 1

    n_pages = max(len(per_page_lines), 1)
    boilerplate = {line for line, cnt in line_counts.items() if cnt >= max(2, n_pages * 0.5)}

    cleaned_pages = []
    for lines in per_page_lines:
        kept = [l for l in lines if l.strip() not in boilerplate]
        cleaned_pages.append("\n".join(kept))

    text = "\n".join(cleaned_pages)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


# ---------- 2. TOPIC EXTRACTION (noun-phrase candidates + TF-IDF / KeyBERT ranking) ----------

META_HEADING_PATTERNS = re.compile(
    r"^(sub\.?\s*code|sub\.?\s*name|unit\s+[ivx\d]+|chapter\s+\d+)", re.IGNORECASE
)


def extract_headings(pdf_path: str) -> list:
    """Primary topic source for structured docs (lecture notes, slides, reports):
    pull lines that are >60% bold text and short enough to be a heading, using
    pdfplumber's per-character font metadata. This is far more reliable than
    statistical extraction when the source document already has real section
    titles -- it directly recovers topics like 'Morphological Analysis' or
    'Word Boundary Detection (Tokenization)' instead of reconstructing them
    statistically from word frequency.
    """
    headings, seen = [], set()
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(extra_attrs=["fontname"])
            lines = {}
            for w in words:
                key = round(w["top"])
                lines.setdefault(key, []).append(w)
            for top, ws in sorted(lines.items()):
                ws_sorted = sorted(ws, key=lambda w: w["x0"])
                bold_count = sum(1 for w in ws_sorted if "Bold" in w["fontname"])
                total = len(ws_sorted)
                if total == 0:
                    continue
                text = " ".join(w["text"] for w in ws_sorted).strip()
                if bold_count / total <= 0.6 or not (1 <= len(text.split()) <= 8):
                    continue
                if META_HEADING_PATTERNS.match(text):
                    continue
                # Real headings don't end in '.' or ',' -- those are almost
                # always word-wrap fragments of a bolded body sentence
                # (e.g. a bullet's last word wrapping onto its own line).
                if text.rstrip().endswith((".", ",")) and not text.rstrip().endswith("?"):
                    continue
                # Headings are Titlecase-ish or a question; skip stray lowercase
                # fragments (another word-wrap symptom) unless short (2 words),
                # since 2-word lowercase noun phrases like "human language" are
                # legitimately used as inline bold emphasis, not junk.
                words = text.split()
                if text[0].islower() and len(words) > 2:
                    continue
                # Clean: drop leading numbering ("1.", "2)"), trailing colons
                clean = re.sub(r"^\d+[\.\)]\s*", "", text)
                clean = re.sub(r"\s*:\s*$", "", clean).strip()
                key_norm = clean.lower()
                if len(clean) < 3 or key_norm in seen:
                    continue
                seen.add(key_norm)
                headings.append(clean)
    return headings


GENERIC_BLOCKLIST = {
    "example", "text", "word", "words", "sentence", "sentences", "concept",
    "process", "step", "steps", "meaning", "information", "output", "input",
    "way", "type", "types", "thing", "things", "task", "tasks", "form",
    "case", "use", "term", "part", "structure", "chapter", "unit", "section",
    "page", "figure", "table", "note", "notes", "summary", "topic", "topics",
    "overview", "introduction", "conclusion", "definition", "diagram",
}


def get_noun_phrase_candidates(text: str) -> list:
    """Use spaCy to pull realistic candidate topics: noun chunks + capitalized
    acronyms (CNN, NLP, LSTM...) that TF-IDF/KeyBERT alone would miss.

    Filtering is done at the TOKEN level using spaCy's own stopword list and
    POS tags -- this is what makes it 'correct' vs. a naive regex/split
    approach, which is what let junk like 'the'/'it'/'that' leak through
    in the first version of this script.
    """
    doc = nlp(text)
    candidates = set()

    for chunk in doc.noun_chunks:
        # Root of the chunk must be a real noun/proper noun, not a pronoun/determiner
        if chunk.root.pos_ not in ("NOUN", "PROPN"):
            continue

        # Strip leading determiners/pronouns/possessives token-by-token
        tokens = [t for t in chunk if not (t.is_stop and t.pos_ in ("DET", "PRON", "ADP"))]
        if not tokens:
            continue

        # Drop the phrase entirely if every remaining token is a stopword
        # or non-alphabetic (numbers, punctuation-only chunks, etc.)
        content_tokens = [t for t in tokens if t.is_alpha and not t.is_stop]
        if not content_tokens:
            continue

        phrase = " ".join(t.text.lower() for t in tokens).strip()
        phrase = re.sub(r"[^a-z0-9\- ]", "", phrase).strip()
        words = phrase.split()

        if not (1 <= len(words) <= 4):
            continue
        if phrase in GENERIC_BLOCKLIST:
            continue
        if all(w in GENERIC_BLOCKLIST for w in words):
            continue

        candidates.add(phrase)

    # Acronyms / all-caps technical terms (CNN, LSTM, NLP, POS, NER...)
    for match in re.finditer(r"\b[A-Z]{2,6}\b", text):
        acr = match.group()
        if acr not in {"I"}:  # ignore the pronoun "I" etc.
            candidates.add(acr.lower())

    return list(candidates)


class TopicExtractor:
    """Ranks noun-phrase candidates by TF-IDF weight against the document.
    Swap in KeyBERT (see USE_KEYBERT below) for embedding-based ranking
    when you have internet access to download the sentence-transformer model."""

    USE_KEYBERT = False  # set True if keybert + internet access to huggingface.co is available

    def __init__(self):
        if self.USE_KEYBERT:
            from keybert import KeyBERT
            self.kw_model = KeyBERT(model="all-MiniLM-L6-v2")

    def extract_from_pdf(self, pdf_path: str, text: str, top_n: int = 8):
        """Preferred entry point: try heading-based extraction (accurate for
        structured docs), fall back to statistical extraction if the PDF has
        no detectable bold headings (e.g. plain scanned/flat text)."""
        headings = extract_headings(pdf_path)
        if len(headings) >= 4:
            return [(h, None) for h in headings[:top_n]]
        return self.extract(text, top_n=top_n)

    def extract(self, text: str, top_n: int = 8):
        candidates = get_noun_phrase_candidates(text)
        if not candidates:
            return []

        if self.USE_KEYBERT:
            results = self.kw_model.extract_keywords(
                text, candidates=candidates, top_n=top_n,
                use_mmr=True, diversity=0.6,
            )
            return results

        # TF-IDF fallback: score each candidate phrase by its frequency in the doc
        vectorizer = TfidfVectorizer(vocabulary=list(set(candidates)), ngram_range=(1, 4))
        try:
            X = vectorizer.fit_transform([text.lower()])
        except ValueError:
            return []
        scores = X.toarray()[0]
        terms = vectorizer.get_feature_names_out()
        ranked = sorted(zip(terms, scores), key=lambda x: -x[1])
        ranked = [(t, s) for t, s in ranked if s > 0]
        return ranked[:top_n]


# ---------- 3. QUESTION GENERATION (template engine) ----------

ACRONYM_TEMPLATES = [
    "Explain in detail about {topic}.",
    "What is {topic} and what is it used for?",
]

CONCEPT_TEMPLATES = [
    "What is {topic}? Explain with a suitable example.",
    "Define {topic} and explain its significance.",
    "Explain the concept of {topic} in detail.",
]

PROCESS_TEMPLATES = [
    "Explain how {topic} works with an example.",
    "Describe the steps involved in {topic}.",
]

COMPARISON_TEMPLATES = [
    "Differentiate between {topic}.",
    "Compare and contrast {topic} with a suitable example.",
]

# Subject-agnostic hints that a topic names a process/technique/method rather
# than a static concept. These are common English morphological patterns for
# "a thing that happens" (works for NLP, biology, chemistry, engineering,
# economics, history...) rather than a fixed domain word list:
#   -tion / -sion   : oxidation, tokenization, integration, diffusion
#   -sis            : photosynthesis, electrolysis, hypothesis
#   -ing            : tagging, segmentation, mining, casting
#   -ment           : fermentation, development, measurement
PROCESS_SUFFIXES = ("tion", "sion", "sis", "ment")
PROCESS_HINT_WORDS = {"process", "method", "technique", "algorithm", "procedure",
                       "mechanism", "cycle", "reaction", "system"}


def _looks_like_process(topic_lower: str) -> bool:
    words = topic_lower.split()
    if any(w in PROCESS_HINT_WORDS for w in words):
        return True
    # last content word ending in a process-y suffix, e.g. "boundary detection",
    # "cellular respiration", "chemical bonding"
    last_word = words[-1] if words else ""
    if last_word.endswith(PROCESS_SUFFIXES) or last_word.endswith("ing"):
        return True
    return False


# Generic acronym detection: ANY bare all-caps token of 2-6 letters (CNN, DNA,
# GDP, RAM, ...) or a heading ending in a parenthetical acronym like
# "Natural Language Understanding (NLU)" or "Deoxyribonucleic Acid (DNA)".
# No fixed subject-specific list -- this is what makes it work across subjects.
_BARE_ACRONYM_RE = re.compile(r"^[A-Z]{2,6}$")
_PAREN_ACRONYM_RE = re.compile(r"\(([A-Z]{2,6})\)\s*$")

# Common all-caps words that are NOT acronyms in this context, so a Titlecase
# heading token like "OF" (rare, but possible in ALL-CAPS PDF headings)
# doesn't get misclassified.
_NON_ACRONYM_WORDS = {"OF", "AND", "THE", "FOR", "ARE", "NOT", "ALL", "ANY"}


class QuestionGenerator:
    def _classify(self, topic: str) -> str:
        low = topic.lower().strip()

        # Heading was already phrased as a question ("What is X?") -> use directly
        if low.startswith(("what is", "how does", "why", "what are", "how do")):
            return "already_question"

        if " and " in low or " vs " in low or "/" in low or " versus " in low:
            return "comparison"

        bare = topic.strip("()").strip()
        if _BARE_ACRONYM_RE.fullmatch(bare) and bare not in _NON_ACRONYM_WORDS:
            return "acronym"
        paren_match = _PAREN_ACRONYM_RE.search(topic)
        if paren_match and paren_match.group(1) not in _NON_ACRONYM_WORDS:
            return "acronym"

        if _looks_like_process(low):
            return "process"
        return "concept"

    def generate(self, topic: str, n: int = 2) -> list:
        kind = self._classify(topic)

        if kind == "already_question":
            base = topic if topic.endswith("?") else topic + "?"
            return [base, f"Explain in detail: {topic.rstrip('?')}."][:n]

        templates = {
            "acronym": ACRONYM_TEMPLATES,
            "process": PROCESS_TEMPLATES,
            "comparison": COMPARISON_TEMPLATES,
            "concept": CONCEPT_TEMPLATES,
        }[kind]

        display_topic = topic
        if kind == "acronym":
            m = _PAREN_ACRONYM_RE.search(topic)
            display_topic = m.group(1) if m else topic.strip("()")

        return [t.format(topic=display_topic) for t in templates[:n]]


# ---------- MAIN PIPELINE ----------

def run_pipeline(pdf_path: str, num_topics: int = 8, questions_per_topic: int = 2):
    print(f"[1/3] Extracting text from: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("No extractable text found (PDF may be scanned/image-based).")
        sys.exit(1)
    print(f"   -> {len(text.split())} words after cleanup")

    print("[2/3] Extracting topics (document headings, with statistical fallback)...")
    topics = TopicExtractor().extract_from_pdf(pdf_path, text, top_n=num_topics)
    print("   Topics found:")
    for phrase, score in topics:
        if score is None:
            print(f"     - {phrase}")
        else:
            print(f"     - {phrase}  (score: {score:.3f})")

    print("[3/3] Generating questions per topic...")
    qg = QuestionGenerator()
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for phrase, _ in topics:
        questions = qg.generate(phrase, n=questions_per_topic)
        print(f"\nTopic: {phrase}")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")

    return topics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path")
    parser.add_argument("--num_topics", type=int, default=8)
    parser.add_argument("--questions_per_topic", type=int, default=2)
    args = parser.parse_args()
    run_pipeline(args.pdf_path, args.num_topics, args.questions_per_topic)
