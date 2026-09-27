import os
import re
import random
import warnings
from typing import List, Dict, Any, Optional

warnings.filterwarnings("ignore", category=FutureWarning)

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from config import GEMINI_API_KEY

if HAS_GENAI and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[QuestionGenerator] Gemini init error: {e}")

# ----------------- Academic Question Templates by Marks & Cognitive Level -----------------

TEMPLATES_2_MARKS = [
    "Define {topic} and state its primary significance in {subject}.",
    "What is meant by {topic}? State its core objective.",
    "State two key advantages and limitations of {topic}.",
    "Mention the fundamental formula or governing equation used in {topic}.",
    "Briefly distinguish between {topic} and conventional baseline techniques.",
    "What role does {topic} play in modern computational pipelines?"
]

TEMPLATES_5_MARKS = [
    "Explain the underlying principles and workflow of {topic} with a suitable illustration.",
    "Describe the mathematical foundation and objective formulation of {topic}.",
    "Outline the sequential algorithmic steps involved in implementing {topic}.",
    "Discuss the trade-offs, hyperparameters, and design choices associated with {topic}.",
    "Explain how {topic} addresses key limitations observed in standard implementations."
]

TEMPLATES_12_MARKS = [
    "Explain the detailed architectural design, functional mechanics, and end-to-end dataflow of {topic} with neat schematic diagrams.",
    "Derive the mathematical formulation of {topic}. Analyze how optimization updates are performed and discuss its computational complexity.",
    "Critically compare {topic} with contemporary alternative approaches. Evaluate performance trade-offs, scalability, and convergence characteristics.",
    "Illustrate the practical implementation of {topic} on a realistic benchmark problem. Detail the pipeline from input ingestion to final inference."
]

TEMPLATES_15_MARKS = [
    "Critically evaluate theoretical frameworks, parameter tuning, and deployment challenges in {topic}. Design an end-to-end enterprise solution addressing edge-case failures.",
    "Formulate a comprehensive architectural pipeline integrating {topic} into a large-scale production system. Discuss fault tolerance, latency budgets, and monitoring metrics."
]

# ----------------- Topic Domain Concept Bank for Intelligent MCQs -----------------
DOMAIN_KNOWLEDGE_BANK = {
    "tokenization": {
        "definition": "Splitting raw text sequences into discrete constituent units (words, subwords, or characters)",
        "distractors": [
            "Assigning grammatical parts of speech to individual words",
            "Reducing inflected words to their root base dictionary form",
            "Eliminating punctuation and non-printable characters only"
        ],
        "key_fact": "Tokenization is the mandatory primary step in NLP pipelines before numerical vectorization.",
        "concept": "Byte-Pair Encoding (BPE) and WordPiece are common subword tokenization algorithms."
    },
    "stemming": {
        "definition": "Heuristic rule-based truncation of word affixes to produce a crude base stem (e.g., Porter Stemmer)",
        "distractors": [
            "Dictionary-based morphological lookup to return grammatically valid root lemmas",
            "Syntactic parsing of dependency relations within sentences",
            "Converting character byte streams into UTF-8 encodings"
        ],
        "key_fact": "Stemming does not guarantee that the resulting stem is a linguistically valid word.",
        "concept": "Over-stemming and under-stemming are common failure modes of algorithmic stemmers."
    },
    "lemmatization": {
        "definition": "Linguistically informed transformation of words into true dictionary lemmas using vocabulary and morphological analysis",
        "distractors": [
            "Crudely chopping word suffixes using fixed character regex patterns",
            "Splitting compound sentences into isolated clause tokens",
            "Generating n-gram character probability distributions"
        ],
        "key_fact": "Lemmatization requires contextual Part-of-Speech (POS) knowledge to resolve ambiguities.",
        "concept": "Words like 'better' lemmatize to 'good', whereas stemmers fail on irregular morphology."
    },
    "morphological analysis": {
        "definition": "Analyzing internal linguistic structure of words comprising morphemes (stems, prefixes, suffixes)",
        "distractors": [
            "Computing phonetic pitch variations in acoustic speech signals",
            "Mapping sentence semantics into multi-dimensional embeddings",
            "Extracting entity boundary positions using named entity recognition"
        ],
        "key_fact": "Morphemes represent the smallest meaningful grammatical units in human language.",
        "concept": "Inflectional morphology modifies grammatical aspects without altering core semantic part of speech."
    },
    "boundary determination": {
        "definition": "Identifying sentence boundaries and word demarcations in raw unformatted corpora",
        "distractors": [
            "Setting hyperparameter boundary thresholds for neural activations",
            "Establishing decision boundaries in support vector margin hyperplanes",
            "Determining gradient clipping limits during backpropagation"
        ],
        "key_fact": "Punctuation ambiguity (e.g. periods in abbreviations vs sentence terminators) complicates boundary detection.",
        "concept": "Rule-based and machine-learned classifiers (such as Punkt) resolve sentence boundary ambiguity."
    },
    "perceptron": {
        "definition": "Fundamental linear binary classification unit computing weighted sum of inputs followed by step activation",
        "distractors": [
            "Multi-layer non-linear network capable of solving arbitrary XOR surfaces directly",
            "Recurrent memory cell maintaining internal gating vectors across time steps",
            "Unsupervised clustering algorithm minimizing intra-cluster variance"
        ],
        "key_fact": "Single-layer perceptrons can only converge on linearly separable decision boundaries.",
        "concept": "Rosenblatt's perceptron convergence theorem guarantees convergence if data is linearly separable."
    },
    "activation functions": {
        "definition": "Non-linear mathematical mappings introduced into neuron outputs to enable learning complex non-linear functions",
        "distractors": [
            "Optimization algorithms adjusting weight parameters along negative gradient vectors",
            "Dimensionality reduction layers compressing feature maps into latent manifolds",
            "Loss functions measuring numerical divergence between predictions and ground truth"
        ],
        "key_fact": "Without non-linear activations, multi-layer networks collapse mathematically to a single linear transformation.",
        "concept": "ReLU solves the vanishing gradient problem in the positive domain but suffers from 'dying ReLU'."
    },
    "gradient descent": {
        "definition": "First-order iterative optimization algorithm that updates parameters in the direction of steepest loss descent",
        "distractors": [
            "Heuristic search technique exploring discrete combinatorial parameter permutations",
            "Matrix decomposition method calculating exact inverse covariance matrices",
            "Sampling algorithm estimating posterior probability distributions via MCMC"
        ],
        "key_fact": "The learning rate alpha determines the step size taken along the gradient negative direction.",
        "concept": "Stochastic Gradient Descent (SGD) and Adam introduce momentum and adaptive learning rates."
    },
    "convolution": {
        "definition": "Mathematical operation sliding spatial filter kernels across multidimensional tensors to produce feature maps",
        "distractors": [
            "Matrix transpose multiplication between dense fully-connected parameter matrices",
            "Element-wise max reduction pooling across disjoint receptive fields",
            "Softmax normalization generating class conditional probability distributions"
        ],
        "key_fact": "Convolution enforces parameter sharing and translation equivariance across spatial dimensions.",
        "concept": "Kernel size, stride, and padding dictate the spatial dimensions of the resulting feature maps."
    }
}


class QuestionGenerator:
    """
    Intelligent Academic Question Paper & Adaptive Assessment Engine.
    Produces Bloom's Taxonomy-aligned question papers and dynamic 4-option MCQs.
    """

    @classmethod
    def _classify_topic(cls, topic: str) -> str:
        low = topic.lower().strip()
        if " vs " in low or " and " in low or " versus " in low or "/" in low:
            return "comparison"
        words = low.split()
        if any(w in {"process", "method", "technique", "algorithm", "procedure", "analysis", "detection", "scheduling", "descent", "propagation", "tuning", "preprocessing", "learning"} for w in words):
            return "process"
        last_word = words[-1] if words else ""
        if last_word.endswith(("tion", "sion", "sis", "ing", "ment")):
            return "process"
        bare = topic.strip("()").strip()
        if re.fullmatch(r"^[A-Z]{2,6}$", bare) or re.search(r"\(([A-Z]{2,6})\)", topic):
            return "acronym"
        return "concept"

    @classmethod
    def rank_important_topics(cls, topics: List[str]) -> List[str]:
        """
        Ranks and filters extracted topics to prioritize the most important,
        pedagogically significant concepts (multi-word technical terms, acronyms, core principles)
        over minor fragments or boilerplate.
        """
        scored = []
        for t in topics:
            clean = cls._clean_topic_name(t)
            if not clean or len(clean) < 3:
                continue
            low = clean.lower()
            # Penalize or skip boilerplate/metadata
            if any(b in low for b in ["advantages:", "disadvantages:", "definition:", "table", "figure", "page"]):
                continue

            score = 10.0
            words = clean.split()
            # Technical multi-word terms (e.g. "Convolutional Neural Networks", "Morphological Analysis")
            if 2 <= len(words) <= 4:
                score += 8.0
            elif len(words) == 1:
                score += 4.0

            # Technical Acronym bonus (e.g. CNN, RNN, BERT, NLP, SGD, LSTM)
            if clean.isupper() or re.search(r"\b[A-Z]{2,6}\b", clean):
                score += 7.0

            # Core technical indicators
            if any(term in low for term in ["network", "neural", "model", "algorithm", "descent", "analysis", "learning", "gradient", "token", "transform", "vector", "layer", "feature", "classification", "regression", "optimization", "pipeline", "attention", "loss", "metric", "embedding"]):
                score += 6.0

            scored.append((clean, score))

        scored.sort(key=lambda x: -x[1])
        seen = set()
        ranked = []
        for term, _ in scored:
            if term.lower() not in seen:
                seen.add(term.lower())
                ranked.append(term)
        return ranked or [cls._clean_topic_name(t) for t in topics if t]

    @classmethod
    def generate_questions_for_topic(cls, topic: str, subject: str = "Deep Learning", n: int = 1, marks: int = 2) -> List[str]:
        """Generates academic theoretical questions tailored to specific marks using What-inquiry formulations."""
        clean_topic = cls._clean_topic_name(topic)
        kind = cls._classify_topic(clean_topic)

        if marks <= 2:
            if kind == "acronym":
                pool = [
                    f"What is {clean_topic} and what is its primary computational role in {subject}?",
                    f"What does {clean_topic} stand for, and what core function does it perform?",
                    f"What are two key advantages and limitations of using {clean_topic}?"
                ]
            elif kind == "process":
                pool = [
                    f"What is {clean_topic}? State the primary problem it addresses in {subject}.",
                    f"What is meant by {clean_topic}? State its core objective.",
                    f"What are the primary operational steps involved in {clean_topic}?"
                ]
            elif kind == "comparison":
                pool = [
                    f"What is the difference between {clean_topic}? Explain with a brief example.",
                    f"What are the primary distinctions and practical trade-offs of {clean_topic}?"
                ]
            else:
                pool = [
                    f"What is {clean_topic}? State its theoretical significance in {subject}.",
                    f"What is meant by {clean_topic}, and what governing principles define it?",
                    f"What role does {clean_topic} perform in modern computational pipelines?"
                ]
        elif marks <= 5:
            if kind == "acronym":
                pool = [
                    f"What is {clean_topic}? Describe its architectural components and operational workflow with a neat diagram.",
                    f"What are the mechanisms through which {clean_topic} enhances representational capability and efficiency in {subject}?"
                ]
            elif kind == "process":
                pool = [
                    f"What is {clean_topic}? Explain the step-by-step workflow, mathematical formulation, and intuition behind it.",
                    f"What are the sequential algorithmic phases, inputs, and outputs associated with {clean_topic}?"
                ]
            elif kind == "comparison":
                pool = [
                    f"What are the critical differences between {clean_topic} in terms of algorithmic complexity and output accuracy?",
                    f"What are the practical trade-offs, advantages, and failure scenarios of {clean_topic}?"
                ]
            else:
                pool = [
                    f"What is {clean_topic}? Explain its theoretical formulation and practical application with an illustration.",
                    f"What are the fundamental properties, parameter sensitivities, and design choices of {clean_topic}?"
                ]
        elif marks <= 12:
            if kind == "acronym":
                pool = [
                    f"What is {clean_topic}? Explain the detailed architectural design, layer operations, and information flow in {clean_topic} with neat schematic diagrams.",
                    f"What are the theoretical formulation, parameter updates, and optimization strategies for {clean_topic}? Critically evaluate its performance."
                ]
            elif kind == "process":
                pool = [
                    f"What is {clean_topic}? Derive the mathematical formulation and sequential algorithmic steps with a step-by-step example walkthrough.",
                    f"What are the operational mechanics, failure modes, and convergence optimization techniques of {clean_topic}? Illustrate with clear diagrams."
                ]
            elif kind == "comparison":
                pool = [
                    f"What are the comprehensive comparative differences in {clean_topic}? Evaluate theoretical foundations, computational efficiency, and practical trade-offs.",
                    f"What are the behavior and performance distinctions of {clean_topic} across varying scale and noise conditions? Support with illustrative scenarios."
                ]
            else:
                pool = [
                    f"What is {clean_topic}? Explain the fundamental principles, mathematical equations, and end-to-end implementation with neat diagrams.",
                    f"What are the theoretical frameworks, parameter tuning dynamics, and deployment challenges in {clean_topic}? Evaluate in detail."
                ]
        else:
            pool = [
                f"What are the engineering challenges, parameter design choices, and failure mode mitigations when implementing {clean_topic} in an end-to-end production pipeline? Provide a detailed architecture and case study.",
                f"What is the comprehensive computational architecture required to integrate {clean_topic} into large-scale production? Discuss latency budgets, scalability, and monitoring metrics."
            ]

        selected = random.sample(pool, min(n, len(pool)))
        return selected

    @classmethod
    def generate_important_questions_for_unit(cls, topics: List[str], unit_number: int, subject: str = "Deep Learning") -> List[Dict[str, Any]]:
        """
        Generates structured 2-mark, 5-mark, and 12-mark questions for a unit.
        Stored with unit data so students can practice directly.
        """
        if not topics:
            topics = [f"Unit {unit_number} Fundamental Concepts", f"Unit {unit_number} Core Principles"]

        questions = []
        for i, t in enumerate(topics[:6]):
            # 2 Marks Question
            q2 = cls.generate_questions_for_topic(t, subject, n=1, marks=2)[0]
            questions.append({
                "unit_number": unit_number,
                "question": q2,
                "topic": t,
                "marks_category": 2,
                "frequency": "High" if i < 3 else "Medium"
            })

            # 5 Marks Question
            q5 = cls.generate_questions_for_topic(t, subject, n=1, marks=5)[0]
            questions.append({
                "unit_number": unit_number,
                "question": q5,
                "topic": t,
                "marks_category": 5,
                "frequency": "High" if i < 2 else "Medium"
            })

            # 12 Marks Question
            if i < 4:
                q12 = cls.generate_questions_for_topic(t, subject, n=1, marks=12)[0]
                questions.append({
                    "unit_number": unit_number,
                    "question": q12,
                    "topic": t,
                    "marks_category": 12,
                    "frequency": "High" if i < 2 else "Medium"
                })

        return questions

    @classmethod
    def _get_topics_for_unit(cls, u_num: int, units_dict: Dict[int, Any], primary_topics: Optional[List[str]] = None, current_unit: int = 1, subject: str = "Deep Learning") -> List[str]:
        """Returns ranked important topics specifically for unit u_num."""
        u_topics = []
        if primary_topics and u_num == current_unit:
            u_topics.extend(primary_topics)

        u_data = units_dict.get(u_num) or units_dict.get(str(u_num)) or {}
        for t in u_data.get("topics", []):
            if t not in u_topics:
                u_topics.append(t)

        ranked = cls.rank_important_topics(u_topics)
        if not ranked:
            ranked = [f"{subject} Unit {u_num} Concept {i}" for i in range(1, 6)]
        return ranked

    @classmethod
    def _extract_pdf_answer_for_topic(cls, topic: str, u_num: int, units_dict: Dict[int, Any], subject: str = "Deep Learning") -> str:
        """
        Extracts authoritative ground truth answer from the uploaded PDF content for this topic.
        """
        u_data = units_dict.get(u_num) or units_dict.get(str(u_num)) or {}
        extracted_text = u_data.get("extracted_text", "")

        # 1. Search paragraphs in extracted_text from uploaded PDF
        if extracted_text:
            paras = [p.strip() for p in extracted_text.split("\n\n") if len(p.strip()) > 30]
            matched_paras = [p for p in paras if topic.lower() in p.lower()]
            if matched_paras:
                return "\n\n".join(matched_paras[:2])

        # 2. Check key concepts in u_data
        for kc in u_data.get("key_concepts", []):
            if topic.lower() in kc.get("name", "").lower():
                return f"{kc.get('name')}: {kc.get('description')}"

        # 3. Check RAG vector store chunks for this subject and unit
        try:
            from services.rag_engine import rag_engine
            chunks = rag_engine.vector_store.get(subject, [])
            topic_chunks = [c["text"] for c in chunks if c.get("unit_number") == u_num and topic.lower() in c.get("topic", "").lower()]
            if topic_chunks:
                return "\n\n".join(topic_chunks[:2])
        except Exception:
            pass

        # 4. Fallback domain reference
        return (
            f"{topic} is an essential technical concept in {subject} (Unit {u_num}). "
            f"It encompasses fundamental governing equations, architectural components, operational algorithms, "
            f"and parameter optimization techniques."
        )

    @classmethod
    def generate_blueprint_paper(cls, subject: str, ia_type: str, units_dict: Dict[int, Any], primary_topics: Optional[List[str]] = None, current_unit: int = 1) -> Dict[str, Any]:
        """
        Auto-generates Blueprint Question Paper based on exact Assessment Type specification:
        - IA 1:
            * Part A: 5 x 2 Marks (Q1-Q5, from Unit 1 & Unit 2)
            * Part B: 4 x 12 Marks in Either/Or pairs (Q6a or Q6b from Unit 1, Q7a or Q7b from Unit 2)
            * Part C: 1 x 16 Marks in Either/Or (Q8a or Q8b)
            * Total: 50 Marks
        - IA 2:
            * Part A: 5 x 2 Marks (Q1-Q5, from Unit 2)
            * Part B: 4 x 12 Marks in Either/Or pairs (Q6a or Q6b from Unit 3, Q7a or Q7b from Unit 3)
            * Part C: 1 x 16 Marks in Either/Or (Q8a or Q8b from Unit 3)
            * Total: 50 Marks
        - IA 3 / Model Exam:
            * Part A: 10 x 2 Marks (Q1-Q10, exactly 2 questions per unit for Units 1 to 5)
            * Part B: 5 x 12 Marks in Either/Or pairs (Q6 to Q10, each from one unit: Q6 Unit 1, Q7 Unit 2, Q8 Unit 3, Q9 Unit 4, Q10 Unit 5)
            * Part C: 1 x 16 Marks in Either/Or (Q11a or Q11b)
            * Total: 96 / 100 Marks
        """
        ia_lower = ia_type.lower()
        questions_list = []
        part_a_list = []
        part_b_list = []
        part_c_list = []

        if "1" in ia_lower:
            exam_name = "Internal Assessment 1"
            total_marks = 50

            u1_topics = cls._get_topics_for_unit(1, units_dict, primary_topics, current_unit, subject)
            u2_topics = cls._get_topics_for_unit(2, units_dict, primary_topics, current_unit, subject)

            # Part A: 5 questions x 2 Marks (Q1-Q3 from Unit 1, Q4-Q5 from Unit 2)
            for idx in range(1, 6):
                u_assigned = 1 if idx <= 3 else 2
                topic_source = u1_topics if u_assigned == 1 else u2_topics
                t = topic_source[(idx - 1) % len(topic_source)]
                q_text = cls.generate_questions_for_topic(t, subject, n=1, marks=2)[0]
                q_obj = {
                    "question_id": f"Q{idx}",
                    "part": "Part A (2 Marks)",
                    "question": q_text,
                    "topic": t,
                    "max_marks": 2,
                    "unit_number": u_assigned,
                    "pdf_answer": cls._extract_pdf_answer_for_topic(t, u_assigned, units_dict, subject)
                }
                questions_list.append(q_obj)
                part_a_list.append(q_obj)

            # Part B: 4 questions in Either/Or (Q6a or Q6b from Unit 1, Q7a or Q7b from Unit 2)
            t6a = u1_topics[0 % len(u1_topics)]
            t6b = u1_topics[1 % len(u1_topics)]
            q6a = {
                "question_id": "Q6a",
                "part": "Part B (12 Marks - Choice A)",
                "question": cls.generate_questions_for_topic(t6a, subject, n=1, marks=12)[0],
                "topic": t6a,
                "max_marks": 12,
                "unit_number": 1,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t6a, 1, units_dict, subject)
            }
            q6b = {
                "question_id": "Q6b",
                "part": "Part B (12 Marks - Choice B)",
                "question": cls.generate_questions_for_topic(t6b, subject, n=1, marks=12)[0],
                "topic": t6b,
                "max_marks": 12,
                "unit_number": 1,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t6b, 1, units_dict, subject)
            }
            questions_list.extend([q6a, q6b])
            part_b_list.append({"question_id": "Q6", "choice": "Either/Or", "option_a": q6a, "option_b": q6b})

            t7a = u2_topics[0 % len(u2_topics)]
            t7b = u2_topics[1 % len(u2_topics)]
            q7a = {
                "question_id": "Q7a",
                "part": "Part B (12 Marks - Choice A)",
                "question": cls.generate_questions_for_topic(t7a, subject, n=1, marks=12)[0],
                "topic": t7a,
                "max_marks": 12,
                "unit_number": 2,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t7a, 2, units_dict, subject)
            }
            q7b = {
                "question_id": "Q7b",
                "part": "Part B (12 Marks - Choice B)",
                "question": cls.generate_questions_for_topic(t7b, subject, n=1, marks=12)[0],
                "topic": t7b,
                "max_marks": 12,
                "unit_number": 2,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t7b, 2, units_dict, subject)
            }
            questions_list.extend([q7a, q7b])
            part_b_list.append({"question_id": "Q7", "choice": "Either/Or", "option_a": q7a, "option_b": q7b})

            # Part C: 1 question in Either/Or (Q8a or Q8b) - 16 Marks
            t8a = u1_topics[2 % len(u1_topics)]
            t8b = u2_topics[2 % len(u2_topics)]
            q8a = {
                "question_id": "Q8a",
                "part": "Part C (16 Marks - Choice A)",
                "question": cls.generate_questions_for_topic(t8a, subject, n=1, marks=16)[0],
                "topic": t8a,
                "max_marks": 16,
                "unit_number": 1,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t8a, 1, units_dict, subject)
            }
            q8b = {
                "question_id": "Q8b",
                "part": "Part C (16 Marks - Choice B)",
                "question": cls.generate_questions_for_topic(t8b, subject, n=1, marks=16)[0],
                "topic": t8b,
                "max_marks": 16,
                "unit_number": 2,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t8b, 2, units_dict, subject)
            }
            questions_list.extend([q8a, q8b])
            part_c_list.append({"question_id": "Q8", "choice": "Either/Or", "option_a": q8a, "option_b": q8b})

        elif "2" in ia_lower:
            exam_name = "Internal Assessment 2"
            total_marks = 50

            # IA 2: For Part A use Unit 2, for Part B use Unit 3!
            u2_topics = cls._get_topics_for_unit(2, units_dict, primary_topics, current_unit, subject)
            u3_topics = cls._get_topics_for_unit(3, units_dict, primary_topics, current_unit, subject)

            # Part A: 5 questions x 2 Marks from Unit 2
            for idx in range(1, 6):
                t = u2_topics[(idx - 1) % len(u2_topics)]
                q_text = cls.generate_questions_for_topic(t, subject, n=1, marks=2)[0]
                q_obj = {
                    "question_id": f"Q{idx}",
                    "part": "Part A (2 Marks)",
                    "question": q_text,
                    "topic": t,
                    "max_marks": 2,
                    "unit_number": 2,
                    "pdf_answer": cls._extract_pdf_answer_for_topic(t, 2, units_dict, subject)
                }
                questions_list.append(q_obj)
                part_a_list.append(q_obj)

            # Part B: 4 questions in Either/Or from Unit 3 (Q6a/Q6b, Q7a/Q7b)
            t6a = u3_topics[0 % len(u3_topics)]
            t6b = u3_topics[1 % len(u3_topics)]
            q6a = {
                "question_id": "Q6a",
                "part": "Part B (12 Marks - Choice A)",
                "question": cls.generate_questions_for_topic(t6a, subject, n=1, marks=12)[0],
                "topic": t6a,
                "max_marks": 12,
                "unit_number": 3,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t6a, 3, units_dict, subject)
            }
            q6b = {
                "question_id": "Q6b",
                "part": "Part B (12 Marks - Choice B)",
                "question": cls.generate_questions_for_topic(t6b, subject, n=1, marks=12)[0],
                "topic": t6b,
                "max_marks": 12,
                "unit_number": 3,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t6b, 3, units_dict, subject)
            }
            questions_list.extend([q6a, q6b])
            part_b_list.append({"question_id": "Q6", "choice": "Either/Or", "option_a": q6a, "option_b": q6b})

            t7a = u3_topics[2 % len(u3_topics)]
            t7b = u3_topics[3 % len(u3_topics)]
            q7a = {
                "question_id": "Q7a",
                "part": "Part B (12 Marks - Choice A)",
                "question": cls.generate_questions_for_topic(t7a, subject, n=1, marks=12)[0],
                "topic": t7a,
                "max_marks": 12,
                "unit_number": 3,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t7a, 3, units_dict, subject)
            }
            q7b = {
                "question_id": "Q7b",
                "part": "Part B (12 Marks - Choice B)",
                "question": cls.generate_questions_for_topic(t7b, subject, n=1, marks=12)[0],
                "topic": t7b,
                "max_marks": 12,
                "unit_number": 3,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t7b, 3, units_dict, subject)
            }
            questions_list.extend([q7a, q7b])
            part_b_list.append({"question_id": "Q7", "choice": "Either/Or", "option_a": q7a, "option_b": q7b})

            # Part C: 1 question in Either/Or (Q8a or Q8b) - 16 Marks from Unit 3
            t8a = u3_topics[4 % len(u3_topics)]
            t8b = u2_topics[0 % len(u2_topics)]
            q8a = {
                "question_id": "Q8a",
                "part": "Part C (16 Marks - Choice A)",
                "question": cls.generate_questions_for_topic(t8a, subject, n=1, marks=16)[0],
                "topic": t8a,
                "max_marks": 16,
                "unit_number": 3,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t8a, 3, units_dict, subject)
            }
            q8b = {
                "question_id": "Q8b",
                "part": "Part C (16 Marks - Choice B)",
                "question": cls.generate_questions_for_topic(t8b, subject, n=1, marks=16)[0],
                "topic": t8b,
                "max_marks": 16,
                "unit_number": 3,
                "pdf_answer": cls._extract_pdf_answer_for_topic(t8b, 3, units_dict, subject)
            }
            questions_list.extend([q8a, q8b])
            part_c_list.append({"question_id": "Q8", "choice": "Either/Or", "option_a": q8a, "option_b": q8b})

        else:
            # IA 3 / Model Exam
            exam_name = "Internal Assessment 3 / Model Exam"
            total_marks = 100

            unit_topics_map = {
                u: cls._get_topics_for_unit(u, units_dict, primary_topics, current_unit, subject)
                for u in range(1, 6)
            }

            # Part A: 10 x 2 Marks (each 2 questions from one unit)
            # Q1, Q2: Unit 1 | Q3, Q4: Unit 2 | Q5, Q6: Unit 3 | Q7, Q8: Unit 4 | Q9, Q10: Unit 5
            q_num = 1
            for u in range(1, 6):
                u_top = unit_topics_map[u]
                for sub_i in range(2):
                    t = u_top[sub_i % len(u_top)]
                    q_text = cls.generate_questions_for_topic(t, subject, n=1, marks=2)[0]
                    q_obj = {
                        "question_id": f"Q{q_num}",
                        "part": "Part A (2 Marks)",
                        "question": q_text,
                        "topic": t,
                        "max_marks": 2,
                        "unit_number": u,
                        "pdf_answer": cls._extract_pdf_answer_for_topic(t, u, units_dict, subject)
                    }
                    questions_list.append(q_obj)
                    part_a_list.append(q_obj)
                    q_num += 1

            # Part B: 5 x 12 Marks (each question from one unit with a or b, from Q6 to Q10)
            # Q6a/b: Unit 1 | Q7a/b: Unit 2 | Q8a/b: Unit 3 | Q9a/b: Unit 4 | Q10a/b: Unit 5
            for b_idx, u in enumerate(range(1, 6), start=6):
                u_top = unit_topics_map[u]
                tb_a = u_top[1 % len(u_top)]
                tb_b = u_top[2 % len(u_top)]
                q_a = {
                    "question_id": f"Q{b_idx}a",
                    "part": f"Part B (12 Marks - Choice A)",
                    "question": cls.generate_questions_for_topic(tb_a, subject, n=1, marks=12)[0],
                    "topic": tb_a,
                    "max_marks": 12,
                    "unit_number": u,
                    "pdf_answer": cls._extract_pdf_answer_for_topic(tb_a, u, units_dict, subject)
                }
                q_b = {
                    "question_id": f"Q{b_idx}b",
                    "part": f"Part B (12 Marks - Choice B)",
                    "question": cls.generate_questions_for_topic(tb_b, subject, n=1, marks=12)[0],
                    "topic": tb_b,
                    "max_marks": 12,
                    "unit_number": u,
                    "pdf_answer": cls._extract_pdf_answer_for_topic(tb_b, u, units_dict, subject)
                }
                questions_list.extend([q_a, q_b])
                part_b_list.append({"question_id": f"Q{b_idx}", "choice": "Either/Or", "unit_number": u, "option_a": q_a, "option_b": q_b})

            # Part C: 1 x 16 Mark question (Q11a or Q11b)
            tc_a = unit_topics_map[3][0 % len(unit_topics_map[3])]
            tc_b = unit_topics_map[4][0 % len(unit_topics_map[4])]
            q11a = {
                "question_id": "Q11a",
                "part": "Part C (16 Marks - Choice A)",
                "question": cls.generate_questions_for_topic(tc_a, subject, n=1, marks=16)[0],
                "topic": tc_a,
                "max_marks": 16,
                "unit_number": 3,
                "pdf_answer": cls._extract_pdf_answer_for_topic(tc_a, 3, units_dict, subject)
            }
            q11b = {
                "question_id": "Q11b",
                "part": "Part C (16 Marks - Choice B)",
                "question": cls.generate_questions_for_topic(tc_b, subject, n=1, marks=16)[0],
                "topic": tc_b,
                "max_marks": 16,
                "unit_number": 4,
                "pdf_answer": cls._extract_pdf_answer_for_topic(tc_b, 4, units_dict, subject)
            }
            questions_list.extend([q11a, q11b])
            part_c_list.append({"question_id": "Q11", "choice": "Either/Or", "option_a": q11a, "option_b": q11b})

        paper_structure = {
            "part_a": part_a_list,
            "part_b": part_b_list,
            "part_c": part_c_list,
            "total_marks": total_marks
        }

        return {
            "subject": subject,
            "exam_name": exam_name,
            "ia_type": ia_type,
            "unit_number": current_unit,
            "total_marks": total_marks,
            "questions": questions_list,
            "paper": paper_structure
        }

    @classmethod
    def generate_mcq_quiz(cls, topics: List[str], subject: str = "Deep Learning", context_chunks: Optional[List[Dict[str, Any]]] = None, count: int = 5) -> List[Dict[str, Any]]:
        """
        Dynamically generates high-quality 4-choice MCQs for the student's weak/moderate topics.
        Uses Gemini LLM if GEMINI_API_KEY is available, or our rich contextual generation engine.
        """
        if not topics:
            topics = [f"{subject} Core Principles", f"{subject} Optimization"]

        # 1. Attempt Gemini generation if key is present
        if HAS_GENAI and GEMINI_API_KEY:
            try:
                gemini_questions = cls._generate_mcq_with_gemini(topics, subject, count)
                if gemini_questions and len(gemini_questions) >= count:
                    return gemini_questions[:count]
            except Exception as e:
                print(f"[QuestionGenerator] Gemini MCQ generation fallback: {e}")

        # 2. Robust Offline Academic MCQ Synthesis Engine
        quiz_items = []
        for topic in topics:
            mcq = cls._synthesize_mcq_for_topic(topic, subject, context_chunks)
            if mcq:
                quiz_items.append(mcq)
            if len(quiz_items) >= count:
                break

        # Fill remaining if needed
        while len(quiz_items) < count:
            t = topics[len(quiz_items) % len(topics)]
            variant_mcq = cls._synthesize_variant_mcq(t, subject)
            quiz_items.append(variant_mcq)

        return quiz_items[:count]

    @classmethod
    def _synthesize_mcq_for_topic(cls, topic: str, subject: str, context_chunks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Synthesizes a precise 4-option MCQ for any given academic topic."""
        clean = cls._clean_topic_name(topic)
        low = clean.lower()

        # Check domain knowledge bank first
        for key, info in DOMAIN_KNOWLEDGE_BANK.items():
            if key in low or low in key:
                correct_text = info["definition"]
                distractors = list(info["distractors"])
                options = [correct_text] + distractors
                # Shuffle options and track correct index
                shuffled = list(options)
                random.shuffle(shuffled)
                correct_idx = shuffled.index(correct_text)
                return {
                    "topic": topic,
                    "question": f"What is the primary function and definition of {clean}?",
                    "options": shuffled,
                    "correct": correct_idx,
                    "explanation": f"{info['key_fact']} {info.get('concept', '')}"
                }

        # Context-based or Procedural Generation
        text_excerpt = ""
        if context_chunks:
            for c in context_chunks:
                if low in c.get("text", "").lower() or low in c.get("topic", "").lower():
                    text_excerpt = c.get("text", "")[:300]
                    break

        # Template-based MCQ patterns
        patterns = [
            {
                "question": f"Which of the following statements most accurately characterizes {clean}?",
                "correct": f"It is a core theoretical method in {subject} designed to optimize representation, feature extraction, or decision boundaries.",
                "distractors": [
                    f"It is a legacy hardware interface used strictly for peripheral storage management in cloud servers.",
                    f"It completely eliminates the requirement for training data or loss computation in machine learning models.",
                    f"It is an unverified heuristic that has been mathematically proven to diverge under all gradient conditions."
                ],
                "explanation": f"{clean} is an essential concept in {subject}. Mastery of this topic is critical for understanding downstream model behavior."
            },
            {
                "question": f"In the context of {subject}, what is the main objective of implementing {clean}?",
                "correct": f"To improve computational efficiency, generalize pattern detection, and minimize predictive error.",
                "distractors": [
                    f"To intentionally inflate computational complexity without altering model accuracy.",
                    f"To convert continuous floating-point weights into unformatted plain text strings.",
                    f"To bypass backpropagation updates and fix parameters to random constants permanently."
                ],
                "explanation": f"Implementing {clean} enables effective optimization and robust generalization across varying inputs."
            },
            {
                "question": f"What potential failure mode or challenge is commonly associated with {clean} if improperly tuned?",
                "correct": f"Suboptimal convergence, numerical instability, or susceptibility to overfitting/underfitting.",
                "distractors": [
                    f"Immediate physical degradation of central processing unit silicon registers.",
                    f"Inability of mathematical equations to produce real number outputs.",
                    f"Automatic deletion of input training datasets from the local disk drive."
                ],
                "explanation": f"Improper hyperparameter configurations or regularization when using {clean} typically leads to convergence and generalization challenges."
            }
        ]

        chosen = random.choice(patterns)
        options = [chosen["correct"]] + chosen["distractors"]
        shuffled = list(options)
        random.shuffle(shuffled)
        correct_idx = shuffled.index(chosen["correct"])

        return {
            "topic": topic,
            "question": chosen["question"],
            "options": shuffled,
            "correct": correct_idx,
            "explanation": chosen["explanation"]
        }

    @classmethod
    def _synthesize_variant_mcq(cls, topic: str, subject: str) -> Dict[str, Any]:
        clean = cls._clean_topic_name(topic)
        correct_opt = f"Analyzing governing mathematical equations and verifying parameter bounds in {clean}"
        options = [
            correct_opt,
            f"Assuming all weight matrices in {clean} must be statically initialized to zero",
            f"Replacing algorithmic optimization in {clean} with manual guess-and-check loops",
            f"Skipping preprocessing and feeding corrupted raw bytes directly to {clean}"
        ]
        shuffled = list(options)
        random.shuffle(shuffled)
        return {
            "topic": topic,
            "question": f"Which best practice is strongly recommended when working with {clean} in {subject}?",
            "options": shuffled,
            "correct": shuffled.index(correct_opt),
            "explanation": f"Verifying formulation, bounds, and learning rate dynamics ensures stable execution of {clean}."
        }

    @classmethod
    def _generate_mcq_with_gemini(cls, topics: List[str], subject: str, count: int) -> List[Dict[str, Any]]:
        import json
        model = genai.GenerativeModel("gemini-1.5-flash")
        topics_str = ", ".join(topics[:6])
        prompt = f"""Generate {count} multiple-choice academic quiz questions for an undergraduate engineering course in "{subject}".
Target the following specific weak topics: {topics_str}.
Return ONLY a valid JSON array of objects. Do not include markdown codeblocks or other text.
Each object must have exactly these keys:
- "topic": name of the target topic
- "question": clear, rigorous academic question string
- "options": an array of exactly 4 plausible answer choice strings
- "correct": integer index (0, 1, 2, or 3) indicating the correct answer in "options"
- "explanation": a concise educational explanation of why the correct option is right
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        if isinstance(data, list):
            return data
        return []

    @staticmethod
    def _clean_topic_name(topic: str) -> str:
        t = re.sub(r"^\d+[\.\)]\s*", "", topic)
        t = re.sub(r"[\u200b\u200c\u200d\uFEFF•▪●○✔\*\-]", "", t).strip()
        return t

