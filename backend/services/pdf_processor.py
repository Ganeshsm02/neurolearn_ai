import os
import re
import json
import statistics
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        nlp = None
    HAS_SPACY = True if nlp else False
except ImportError:
    HAS_SPACY = False
    nlp = None

from services.question_generator import QuestionGenerator

META_HEADING_PATTERNS = re.compile(
    r"^(sub\.?\s*code|sub\.?\s*name|subject\s*code|department\s*of|faculty\s*of|page\s*\d+|figure\s*\d+|table\s*\d+|prepared\s*by|verified\s*by|lecture\s*notes|academic\s*year)",
    re.IGNORECASE
)

SYLLABUS_START_PATTERNS = re.compile(
    r"^(syllabus|course\s*outcomes?|course\s*objectives?|contents?|unit\s*[ivx\d]+\s*contents?|topics?)\s*[:\-]",
    re.IGNORECASE
)

GENERIC_BLOCKLIST = {
    "example", "examples", "text", "texts", "word", "words", "sentence", "sentences",
    "concept", "concepts", "process", "processes", "step", "steps", "meaning",
    "information", "output", "input", "outputs", "inputs", "way", "ways", "type", "types",
    "thing", "things", "task", "tasks", "form", "forms", "case", "cases", "use", "uses",
    "term", "terms", "part", "parts", "structure", "structures", "chapter", "unit",
    "section", "sections", "page", "pages", "figure", "figures", "table", "tables",
    "note", "notes", "summary", "topic", "topics", "overview", "introduction",
    "conclusion", "definition", "definitions", "diagram", "diagrams", "approach",
    "approaches", "method", "methods", "technique", "techniques", "result", "results",
    "detail", "details", "problem", "problems", "solution", "solutions", "model", "models",
    "various", "following", "given", "above", "below", "different", "similar", "general",
    "simple", "important", "basic", "main", "primary", "secondary", "order", "level",
    "levels", "system", "systems", "function", "functions", "feature", "features",
    "value", "values", "number", "numbers", "data", "point", "points", "line", "lines"
}


def sanitize_text(text: str) -> str:
    """Cleans zero-width characters, non-printable unicode, and normalizes quotes/dashes."""
    if not text:
        return ""
    # Remove zero-width spaces and formatting bytes
    text = re.sub(r"[\u200b\u200c\u200d\uFEFF\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    # Normalize bullet markers
    text = re.sub(r"[\u2022\u25cf\u25aa\u25ab\u25cb\u2714\u2605\u2731\u2023\u2043\u2219]", " ", text)
    # Normalize quotes and dashes
    text = re.sub(r"[\u201c\u201d\u201e\u201f\u00ab\u00bb]", '"', text)
    text = re.sub(r"[\u2018\u2019\u201a\u201b]", "'", text)
    text = re.sub(r"[\u2013\u2014\u2015]", "-", text)
    # Normalize excessive spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


class PDFProcessor:
    """
    High-Speed & Intelligent Academic PDF Topic Extraction Engine.
    Powered by PyMuPDF (fitz) with automatic font geometry analysis,
    syllabus outline parsing, and SpaCy NLP candidate extraction.
    """

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """High-speed text extractor with boilerplate header/footer filtering."""
        if not pdf_path or not os.path.exists(pdf_path):
            return ""

        pages_text = []

        if HAS_PYMUPDF:
            try:
                doc = fitz.open(pdf_path)
                for page in doc:
                    raw = page.get_text("text")
                    cleaned = sanitize_text(raw)
                    if cleaned:
                        pages_text.append(cleaned)
                doc.close()
            except Exception as e:
                print(f"[PDFProcessor] PyMuPDF extract warning: {e}")

        # Fallback to pdfplumber if PyMuPDF was unable to read
        if not pages_text and HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        raw = page.extract_text()
                        if raw:
                            pages_text.append(sanitize_text(raw))
            except Exception as e:
                print(f"[PDFProcessor] pdfplumber fallback warning: {e}")

        if not pages_text:
            return ""

        # Remove recurring header/footer boilerplate (>40% of pages)
        line_counts = Counter()
        per_page_lines = [p.split("\n") for p in pages_text]
        for lines in per_page_lines:
            for line in set(l.strip() for l in lines if len(l.strip()) > 3):
                line_counts[line] += 1

        n_pages = max(len(per_page_lines), 1)
        boilerplate = {line for line, cnt in line_counts.items() if cnt >= max(2, n_pages * 0.4)}

        cleaned_pages = []
        for lines in per_page_lines:
            kept = [l for l in lines if l.strip() not in boilerplate]
            cleaned_pages.append("\n".join(kept))

        full_text = "\n".join(cleaned_pages)
        full_text = re.sub(r"\n{3,}", "\n\n", full_text)
        return full_text.strip()

    @staticmethod
    def extract_syllabus_topics(text: str) -> List[str]:
        """
        Detects explicit syllabus sections (e.g. 'Syllabus: Topic A - Topic B - Topic C')
        commonly found on the first 1-3 pages of academic lecture notes.
        """
        syllabus_topics = []
        lines = text.split("\n")[:80]  # Examine first 80 lines

        for i, line in enumerate(lines):
            line_clean = sanitize_text(line).strip()
            match = SYLLABUS_START_PATTERNS.match(line_clean)
            if match:
                # Capture remainder of this line + subsequent 2-3 lines if continuous
                content_lines = [re.sub(r"^(syllabus|course\s*outcomes?|course\s*objectives?|contents?|unit\s*[ivx\d]+\s*contents?|topics?)\s*[:\-]\s*", "", line_clean, flags=re.IGNORECASE)]
                for next_line in lines[i+1:i+5]:
                    n_clean = sanitize_text(next_line).strip()
                    if not n_clean or META_HEADING_PATTERNS.match(n_clean) or SYLLABUS_START_PATTERNS.match(n_clean):
                        break
                    # If line starts with bullet or number or dash, add it
                    content_lines.append(n_clean)

                combined = " ".join(content_lines)
                # Split by dash, comma, semicolon, bullet or newline
                parts = re.split(r"[-–—,;\n•●▪]|\s{2,}", combined)
                for p in parts:
                    clean_p = re.sub(r"^\d+[\.\)]\s*", "", p).strip()
                    clean_p = re.sub(r"^[\u200b\u200c\u200d\uFEFF•▪●○✔\*\-]", "", clean_p).strip()
                    clean_p = re.sub(r"\s*:\s*$", "", clean_p).strip()
                    words = clean_p.split()
                    if 1 <= len(words) <= 6 and len(clean_p) >= 3:
                        if clean_p.lower() not in GENERIC_BLOCKLIST and not clean_p.isdigit():
                            syllabus_topics.append(clean_p.title())

                if syllabus_topics:
                    break

        return list(dict.fromkeys(syllabus_topics))

    @staticmethod
    def extract_headings(pdf_path: str) -> List[str]:
        """
        Fast heading detection using PyMuPDF font sizes, weights, and layout geometry.
        Runs in < 0.2 seconds and extracts true section titles without hanging.
        """
        if not HAS_PYMUPDF or not pdf_path or not os.path.exists(pdf_path):
            return []

        headings = []
        seen = set()

        try:
            doc = fitz.open(pdf_path)
            font_sizes = []

            # 1. Sample font sizes to identify average body font size
            sample_pages = doc[:min(10, len(doc))]
            for page in sample_pages:
                d = page.get_text("dict")
                for b in d.get("blocks", []):
                    for l in b.get("lines", []):
                        for s in l.get("spans", []):
                            txt = sanitize_text(s.get("text", "")).strip()
                            if len(txt) > 5 and not txt.isdigit():
                                font_sizes.append(s.get("size", 10.0))

            body_size = statistics.median(font_sizes) if font_sizes else 10.0

            # 2. Extract lines matching heading characteristics
            for page in doc:
                d = page.get_text("dict")
                for b in d.get("blocks", []):
                    if "lines" not in b:
                        continue
                    for l in b.get("lines", []):
                        spans = l.get("spans", [])
                        raw_line_text = " ".join(s.get("text", "") for s in spans).strip()
                        line_text = sanitize_text(raw_line_text).strip()

                        if not line_text or len(line_text) < 3 or len(line_text) > 80:
                            continue

                        # Filter out metadata lines
                        if META_HEADING_PATTERNS.match(line_text):
                            continue

                        # Headings don't end in full stops or commas
                        if line_text.endswith((".", ",")) and not line_text.endswith("?"):
                            continue

                        # Check if line has heading signals:
                        # a) Font size noticeably larger than body text
                        max_size = max((s.get("size", 0.0) for s in spans), default=0.0)
                        is_large = max_size >= (body_size * 1.15)

                        # b) Font is bold (flag & 16 or font name has 'bold')
                        is_bold = any(
                            (s.get("flags", 0) & 16 != 0) or ("bold" in s.get("font", "").lower())
                            for s in spans
                        )

                        # c) Academic numbered heading (e.g. "1.1 Recurrent Neural Networks")
                        is_numbered = bool(re.match(r"^\d+(\.\d+)*\s+[A-Z]", line_text))

                        # d) Title Case or ALL CAPS
                        is_title_or_caps = line_text.isupper() or (line_text[0].isupper() and not line_text.endswith("."))

                        words = line_text.split()
                        if not (1 <= len(words) <= 8):
                            continue

                        if (is_large or is_bold or is_numbered) and is_title_or_caps:
                            # Clean leading numbers and symbols
                            clean = re.sub(r"^\d+[\.\)]\s*", "", line_text)
                            clean = re.sub(r"^\d+(\.\d+)+\s*", "", clean)
                            clean = re.sub(r"\s*:\s*$", "", clean).strip()

                            # If formatted as question, extract core subject
                            q_match = re.match(r"^(what\s+is|what\s+are|how\s+does|why\s+is|explain)\s+(.+?)[\?\.]*$", clean, re.IGNORECASE)
                            if q_match:
                                clean = q_match.group(2).strip()

                            key = clean.lower()
                            if len(clean) >= 3 and key not in seen and key not in GENERIC_BLOCKLIST:
                                # Don't add if all words in blocklist
                                if not all(w.lower() in GENERIC_BLOCKLIST for w in clean.split()):
                                    seen.add(key)
                                    headings.append(clean.title())

            doc.close()
        except Exception as e:
            print(f"[PDFProcessor] PyMuPDF heading extraction error: {e}")

        return headings

    @staticmethod
    def get_noun_phrase_candidates(text: str) -> List[str]:
        """Extracts technical noun chunks and capitalized acronyms using SpaCy."""
        candidates = set()

        # Acronyms (e.g., CNN, RNN, LSTM, NLP, BERT, SGD, RAG, API)
        for match in re.finditer(r"\b[A-Z]{2,6}\b", text):
            acr = match.group()
            if acr not in {"I", "A", "AN", "THE", "FOR", "AND", "NOT", "BUT", "OR"}:
                candidates.add(acr)

        if not nlp:
            # Fallback regex extraction if spaCy model unavailable
            for m in re.finditer(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b", text):
                p = m.group().strip()
                if p.lower() not in GENERIC_BLOCKLIST:
                    candidates.add(p)
            return list(candidates)

        # Process first 60k characters with SpaCy
        doc = nlp(text[:60000])
        for chunk in doc.noun_chunks:
            if chunk.root.pos_ not in ("NOUN", "PROPN"):
                continue

            tokens = [t for t in chunk if not (t.is_stop and t.pos_ in ("DET", "PRON", "ADP"))]
            if not tokens:
                continue

            content_tokens = [t for t in tokens if t.is_alpha and not t.is_stop]
            if not content_tokens:
                continue

            phrase = " ".join(t.text for t in tokens).strip()
            phrase = re.sub(r"[^a-zA-Z0-9\- ]", "", phrase).strip()
            words = phrase.split()

            if not (1 <= len(words) <= 4):
                continue
            if phrase.lower() in GENERIC_BLOCKLIST:
                continue
            if all(w.lower() in GENERIC_BLOCKLIST for w in words):
                continue

            candidates.add(phrase.title())

        return list(candidates)

    @classmethod
    def extract_topics_smart(
        cls,
        raw_text: str,
        pdf_path: Optional[str] = None,
        top_n: int = 10,
        subject_name: Optional[str] = None,
        unit_number=1,
        layout_headings: Optional[List[str]] = None,
        use_llm=None,
        use_clustering=None
    ) -> List[str]:
        """
        Multi-signal topic extraction pipeline:
        1. Syllabus Section Topics (Highest Precision)
        2. Document Visual Headings (PyMuPDF Font & Weight Geometry)
        3. SpaCy Technical Noun Chunks + Acronyms with Frequency & Length Weighting
        """
        combined_scored = {}

        # 1. Syllabus detection
        syllabus_topics = []
        if raw_text:
            syllabus_topics = cls.extract_syllabus_topics(raw_text)
            for t in syllabus_topics:
                combined_scored[t] = combined_scored.get(t, 0) + 50.0  # Top priority

        # 2. Document Headings
        headings = layout_headings or []
        if not headings and pdf_path and os.path.exists(pdf_path):
            headings = cls.extract_headings(pdf_path)

        for h in headings:
            combined_scored[h] = combined_scored.get(h, 0) + 20.0

        # 3. Noun Chunks & Acronyms
        if raw_text:
            candidates = cls.get_noun_phrase_candidates(raw_text)
            low_text = raw_text.lower()
            for c in candidates:
                c_low = c.lower()
                freq = low_text.count(c_low)
                if freq > 0:
                    score = min(freq * 1.5, 15.0)
                    # Length bonus for multi-word technical terms
                    if len(c.split()) >= 2:
                        score += 3.0
                    if c.isupper():
                        score += 5.0
                    combined_scored[c] = combined_scored.get(c, 0) + score

        if not combined_scored:
            return cls._get_kb_fallback_topics(subject_name or "Deep Learning", int(unit_number))[:top_n]

        # Sort by score descending
        sorted_candidates = sorted(combined_scored.items(), key=lambda x: -x[1])

        # Filter near duplicates / substrings
        final_topics = []
        seen_stems = set()

        for term, _ in sorted_candidates:
            term_clean = term.strip()
            term_low = term_clean.lower()
            if len(term_clean) < 3 or term_low in GENERIC_BLOCKLIST:
                continue

            # Check for overlap with already chosen topics
            is_sub = False
            for existing in final_topics:
                e_low = existing.lower()
                if term_low == e_low or (len(term_low) > 4 and term_low in e_low) or (len(e_low) > 4 and e_low in term_low):
                    is_sub = True
                    break

            if not is_sub:
                final_topics.append(term_clean)

            if len(final_topics) >= top_n:
                break

        # Fallback if fewer than 4 topics were found
        if len(final_topics) < 4:
            kb = cls._get_kb_fallback_topics(subject_name or "Deep Learning", int(unit_number))
            for k in kb:
                if k not in final_topics:
                    final_topics.append(k)
                if len(final_topics) >= top_n:
                    break

        return final_topics[:top_n]

    @classmethod
    def analyze_unit_content(
        cls,
        pdf_path: Optional[str],
        subject_name: str,
        unit_number: int,
        raw_text: Optional[str] = None,
        use_llm=None,
        use_clustering=None
    ) -> Dict[str, Any]:
        """
        Comprehensive unit analysis:
        - Extracts primary topics & headings
        - Generates subtopics & contextual key concepts
        - Automatically synthesizes Important Questions for the unit (2, 5, 12 marks)
        """
        full_text = ""
        headings = []

        if pdf_path and os.path.exists(pdf_path):
            full_text = cls.extract_text_from_pdf(pdf_path)
            headings = cls.extract_headings(pdf_path)

        if not full_text:
            full_text = raw_text or ""

        topics = cls.extract_topics_smart(
            full_text,
            pdf_path=pdf_path,
            top_n=10,
            subject_name=subject_name,
            unit_number=unit_number,
            layout_headings=headings
        )

        unit_title = f"Unit {unit_number}: {topics[0]} & Core Methodologies" if topics else f"Unit {unit_number}: Core Principles"

        # Generate realistic subtopics
        subtopics = []
        for t in topics[:6]:
            subtopics.append(f"{t} Formulation & Architecture")
            subtopics.append(f"Practical Implementation of {t}")

        # Extract contextual key concepts with summary definitions from text
        key_concepts = []
        low_text = full_text.lower()
        for t in topics[:6]:
            t_low = t.lower()
            idx = low_text.find(t_low)
            desc = ""
            if idx != -1:
                snippet = full_text[idx:idx+250].replace("\n", " ").strip()
                # Find sentence boundary
                s_end = snippet.find(".")
                if s_end != -1 and s_end > 20:
                    desc = snippet[:s_end+1].strip()
                else:
                    desc = snippet[:150].strip() + "..."
            if not desc:
                desc = f"Core theoretical concept for {t} derived from Unit {unit_number} syllabus."

            key_concepts.append({
                "name": t,
                "description": desc
            })

        # AUTO-GENERATE IMPORTANT QUESTIONS FOR ALL MARKS CATEGORIES (2, 5, 12 Marks)
        important_questions = QuestionGenerator.generate_important_questions_for_unit(
            topics=topics,
            unit_number=int(unit_number),
            subject=subject_name
        )

        return {
            "subject": subject_name,
            "unit_number": int(unit_number),
            "unit_title": unit_title,
            "topics": topics,
            "subtopics": subtopics[:8],
            "key_concepts": key_concepts,
            "important_questions": important_questions,
            "raw_text_length": len(full_text)
        }

    @staticmethod
    def _get_kb_fallback_topics(subject: str, unit_number: int) -> List[str]:
        kb = {
            "Deep Learning": {
                1: ["Perceptron Model Architecture", "Activation Functions (Sigmoid, ReLU, Tanh)", "Gradient Descent Optimization", "Multilayer Perceptron & Backpropagation", "Loss Functions & Cross-Entropy", "Learning Rate Scheduling"],
                2: ["CNN Spatial Feature Maps", "Convolution Kernels & Stride Parameters", "Pooling Operations (Max & Average Pooling)", "AlexNet & VGG Network Backbones", "ResNet Skip Connections", "Batch Normalization Layers"],
                3: ["RNN Sequence Processing & Unrolling", "LSTM Memory Cells & Cell State Persistence", "LSTM Gating Mechanisms (Forget, Input, Output)", "GRU Gated Recurrent Units", "Bidirectional RNN Architectures", "Sequence-to-Sequence Encoders"],
                4: ["Autoencoder Bottleneck Architecture", "Variational Autoencoders (VAE) & KL Divergence", "Latent Space Dimensionality Reduction", "Convolutional Denoising Autoencoders", "Reconstruction Loss Minimization", "Generative Latent Representation"],
                5: ["Generative Adversarial Networks (GAN)", "Generator vs Discriminator Minimax Game", "Self-Attention Mechanism & Query-Key-Value Vectors", "Multi-Head Transformer Architecture", "Positional Encodings", "Transformer Encoder-Decoder Layers"]
            },
            "Machine Learning": {
                1: ["Linear Regression & OLS Cost Function", "Logistic Regression & Sigmoid Curve", "Decision Trees & Gini Impurity", "Bias-Variance Tradeoff & Regularization", "L1 Lasso & L2 Ridge Regularization", "Gradient Descent Weight Updates"],
                2: ["Support Vector Machines (SVM) & Margins", "SVM Kernel Functions (RBF, Polynomial)", "Random Forests & Bagging Ensembles", "Gradient Boosting & XGBoost Framework", "K-Nearest Neighbors (KNN) Distance Metrics", "Ensemble Stacking & Voting"],
                3: ["K-Means Clustering & Elbow Analysis", "Hierarchical Agglomerative Clustering", "Principal Component Analysis (PCA) & Eigenvalues", "t-SNE High-Dimensional Visualization", "DBSCAN Density-Based Clustering", "Silhouette Score Metric"],
                4: ["Confusion Matrix, Precision & Recall", "ROC Curve & AUC Score", "Grid Search & Random Search CV", "K-Fold Cross Validation", "F1-Score & Macro/Micro Averages", "Hyperparameter Tuning Strategies"],
                5: ["Markov Decision Process (MDP)", "Q-Learning & Bellman Optimality Equation", "Policy Gradient Methods", "Model Deployment & Flask REST API", "MLOps Pipelines & Monitoring", "Model Serialization & Pickle/ONNX"]
            },
            "Natural Language Processing (NLP)": {
                1: ["Text Preprocessing & Tokenization", "Stemming & Lemmatization Techniques", "Morphological Analysis & Morphemes", "Boundary Determination in Sentences", "Bag-of-Words & TF-IDF Representations", "Word Embeddings (Word2Vec & GloVe)"],
                2: ["Recurrent Neural Networks for Text", "Bidirectional LSTM Sequence Tagging", "Seq2Seq Encoder-Decoder Framework", "Attention Mechanism & Alignment Scores", "Beam Search Decoding", "BLEU & ROUGE Evaluation Metrics"],
                3: ["Self-Attention & Scaled Dot-Product", "Multi-Head Attention Layers", "Transformer Encoder & Decoder Stacks", "Positional Encodings (Sinusoidal & Learned)", "Masked Attention for Generation", "Layer Normalization & Residuals"],
                4: ["BERT Masked Language Modeling", "GPT Causal Auto-regressive Generation", "T5 Text-to-Text Framework", "Fine-Tuning Strategies (LoRA & PEFT)", "Prompt Engineering & In-Context Learning", "Instruction Tuning & Alignment"],
                5: ["Retrieval-Augmented Generation (RAG)", "Vector Databases & Embeddings Search", "Named Entity Recognition (NER)", "Dependency Parsing & Syntax Trees", "Sentiment Analysis & Opinion Mining", "Cross-Lingual Language Models"]
            },
            "Cloud Computing & Application Development (CCAD)": {
                1: ["Cloud Service Models (IaaS, PaaS, SaaS)", "Virtualization & Hypervisor Architecture", "Cloud Infrastructure Provisioning", "Multi-Tenant Cloud Security", "Elastic Resource Scaling", "Cloud Network Gateways"],
                2: ["Microservices Architecture & API Gateways", "Containerization with Docker", "Kubernetes Pod Orchestration & Scaling", "Serverless Computing (AWS Lambda)", "Event-Driven Microservices", "Service Mesh (Istio)"],
                3: ["Cloud Relational Databases (RDS)", "NoSQL Document Stores (MongoDB/DynamoDB)", "Distributed Caching (Redis/Memcached)", "Cloud Object Storage & Buckets", "Data Replication & Consistency", "Database Sharding"],
                4: ["Cloud Security IAM Policies & Roles", "VPC Private Subnets & Security Groups", "Cloud Monitoring & Logging (CloudWatch)", "Disaster Recovery & Backup Strategies", "Compliance & Encryption Standards", "Zero Trust Cloud Security"],
                5: ["DevOps Automation Pipelines", "Infrastructure as Code (Terraform/Ansible)", "CI/CD Deployment Staging", "Cloud Cost Optimization & Management", "Cloud Native Application Design", "Hybrid Cloud Integration"]
            },
            "MLOps": {
                1: ["ML Lifecycle & Pipeline Automation", "Model Versioning & Experiment Tracking", "Feature Stores & Data Governance", "Continuous Integration for ML (CI/CD)", "Artifact Registries", "Reproducible ML Pipelines"],
                2: ["Data Drift Detection & Monitoring", "Automated Data Validation Schemas", "ETL Pipeline Orchestration", "Feature Engineering Workflows", "Data Profiling & Quality Checks", "Schema Evolution & Lineage"],
                3: ["Distributed Model Training", "Automated Hyperparameter Optimization", "Model Registry & Deployment Artifacts", "Containerization with Docker & Kubernetes", "GPU Cluster Orchestration", "Distributed Training Frameworks"],
                4: ["REST & gRPC Inference Endpoints", "Canary & Shadow Deployment Strategies", "Model Monitoring & Concept Drift", "Latency & Throughput Optimization", "Blue-Green Deployment Pipelines", "Load Balancing & Auto-Scaling"],
                5: ["Model Governance & Auditability", "Fairness & Bias Audit Pipelines", "Cost Optimization & Cloud Resources", "Incident Response & Failure Recovery", "Model Explainability (SHAP/LIME)", "Compliance & Security Safeguards"]
            }
        }

        subject_kb = kb.get(subject, {})
        unit_kb = subject_kb.get(unit_number, None)

        if unit_kb:
            return unit_kb
        else:
            return [
                f"{subject} Unit {unit_number} Fundamental Concepts",
                f"{subject} Unit {unit_number} Optimization Methods",
                f"{subject} Unit {unit_number} Model Architectures",
                f"{subject} Unit {unit_number} Theoretical Principles",
                f"{subject} Unit {unit_number} System Integration",
                f"{subject} Unit {unit_number} Performance Evaluation"
            ]

    @classmethod
    def validate_pdf_content(
        cls,
        pdf_path: Optional[str],
        selected_subject: str,
        selected_unit_number: int,
        raw_text: Optional[str] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates that an uploaded PDF actually matches the selected Subject and Unit Number.
        Prevents uploading Cloud Computing Unit 5 notes when Deep Learning Unit 1 is selected.
        """
        filename = os.path.basename(pdf_path).lower() if pdf_path else ""
        extracted_text = cls.extract_text_from_pdf(pdf_path) if (pdf_path and os.path.exists(pdf_path)) else (raw_text or "")
        text_lower = (filename + " " + extracted_text[:12000]).lower()

        # Subject keyword signatures
        subject_signatures = {
            "Deep Learning": ["deep learning", "neural network", "perceptron", "cnn", "convolutional", "rnn", "lstm", "autoencoder", "backpropagation", "activation function", "vgg", "resnet", "alexnet"],
            "Machine Learning": ["machine learning", "regression", "logistic", "decision tree", "random forest", "svm", "support vector", "clustering", "k-means", "pca", "gradient boosting", "xgboost"],
            "MLOps": ["mlops", "model monitoring", "feature store", "data drift", "model registry", "pipeline automation", "experiment tracking", "containerization", "canary", "shadow deployment"],
            "Cloud Computing & Application Development (CCAD)": ["cloud computing", "virtualization", "hypervisor", "docker", "kubernetes", "microservices", "iaas", "paas", "saas", "aws", "gcp", "azure", "cloud provider", "virtual machine", "cloud consumer", "private cloud"],
            "NLP & Generative AI": ["natural language", "nlp", "tokenization", "lemmatization", "stemming", "transformer", "bert", "gpt", "rag", "retrieval augmented", "word embedding", "morpheme", "seq2seq"]
        }

        # 1. Check for explicit mismatch with another subject signature
        detected_other_subject = None
        selected_sig = subject_signatures.get(selected_subject, [])
        selected_matches = [k for k in selected_sig if k in text_lower]

        for sub_name, keywords in subject_signatures.items():
            if sub_name.lower() != selected_subject.lower():
                matches = [k for k in keywords if k in text_lower]
                if len(matches) >= 2 and len(selected_matches) == 0:
                    detected_other_subject = sub_name
                    break

        # 2. Check for explicit unit number mismatch in PDF text / filename (e.g., "Unit 5", "Unit V", "Unit-5")
        unit_roman_map = {
            1: ["unit 1", "unit i", "unit-1", "unit_1", "unit 01"],
            2: ["unit 2", "unit ii", "unit-2", "unit_2", "unit 02"],
            3: ["unit 3", "unit iii", "unit-3", "unit_3", "unit 03"],
            4: ["unit 4", "unit iv", "unit-4", "unit_4", "unit 04"],
            5: ["unit 5", "unit v", "unit-5", "unit_5", "unit 05"]
        }

        detected_other_unit = None
        selected_unit_patterns = unit_roman_map.get(int(selected_unit_number), [])
        has_selected_unit_mention = any(p in text_lower for p in selected_unit_patterns)

        for u_num, u_patterns in unit_roman_map.items():
            if u_num != int(selected_unit_number):
                if any(p in text_lower for p in u_patterns):
                    if not has_selected_unit_mention:
                        detected_other_unit = u_num
                        break

        if detected_other_subject:
            msg = f"❌ Subject Mismatch: You selected '{selected_subject}', but the uploaded file appears to be for '{detected_other_subject}'."
            if detected_other_unit:
                msg += f" (Specifically Unit {detected_other_unit})"
            msg += f". Please upload PDF notes matching '{selected_subject} (Unit {selected_unit_number})' or change your selected subject to '{detected_other_subject}'."
            return False, msg, {"detected_subject": detected_other_subject, "detected_unit": detected_other_unit}

        if detected_other_unit and not has_selected_unit_mention:
            msg = f"❌ Unit Mismatch: You selected Unit {selected_unit_number} for '{selected_subject}', but the uploaded file ('{filename}') appears to be for Unit {detected_other_unit}. Please upload a PDF for Unit {selected_unit_number} or change the Unit selector to Unit {detected_other_unit}."
            return False, msg, {"detected_subject": selected_subject, "detected_unit": detected_other_unit}

        return True, "PDF matches selected subject and unit.", {"detected_subject": selected_subject, "detected_unit": selected_unit_number}


