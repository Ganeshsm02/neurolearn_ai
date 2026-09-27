import os
import sys

# Ensure backend directory is on Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_adapter

def seed_database():
    print("[Seed Engine] Seeding all 5 Units (Unit 1 to Unit 5), question mappings & student marks...")

    subjects = [
        "Deep Learning",
        "Machine Learning",
        "MLOps",
        "Cloud Computing & Application Development (CCAD)",
        "NLP & Generative AI"
    ]

    unit_titles = {
        1: "Core Foundations & Fundamental Models",
        2: "Advanced Architectures & Feature Extraction",
        3: "Sequence Models, Optimization & Fine-Tuning",
        4: "Unsupervised Learning, Autoencoders & Representation",
        5: "Generative Models, Transformers & Enterprise Deployment"
    }

    topics_pool = {
        "Deep Learning": {
            1: ["Perceptron Model", "Activation Functions", "Gradient Descent", "Multilayer Perceptron (MLP)"],
            2: ["CNN Architecture", "Convolution & Pooling", "AlexNet & VGG", "ResNet & Skip Connections"],
            3: ["RNN Architecture", "LSTM Networks", "GRU Gated Units", "Bidirectional RNN"],
            4: ["Autoencoder Architecture", "Variational Autoencoders (VAE)", "Dimensionality Reduction", "Latent Space Representation"],
            5: ["Generative Adversarial Networks (GAN)", "Generator vs Discriminator", "Self-Attention Mechanism", "Transformer Architecture"]
        }
    }

    # Seed all 5 units for all 5 subjects
    for sub in subjects:
        sub_topics = topics_pool.get(sub, {})
        for u_num in range(1, 6):
            t_list = sub_topics.get(u_num, [
                f"{sub} Unit {u_num} Theoretical Core",
                f"{sub} Unit {u_num} Practical Implementation",
                f"{sub} Unit {u_num} Optimization & Tuning",
                f"{sub} Unit {u_num} Industry Applications"
            ])

            unit_doc = {
                "subject": sub,
                "unit_number": u_num,
                "unit_title": f"Unit {u_num}: {unit_titles[u_num]}",
                "topics": t_list,
                "subtopics": [f"Subtopic for {t}" for t in t_list[:4]],
                "key_concepts": [
                    {"name": t_list[0], "description": f"Core theoretical principle for {t_list[0]}."},
                    {"name": t_list[1], "description": f"Practical application guide for {t_list[1]}."}
                ],
                "important_questions": [
                    {"question": f"Explain the architecture and mathematical formulation of {t_list[0]} in detail.", "marks_category": 10, "frequency": "High"},
                    {"question": f"Differentiate between {t_list[0]} and {t_list[1]} with suitable diagrams.", "marks_category": 5, "frequency": "High"},
                    {"question": f"Discuss the key challenges and optimization strategies in {t_list[2] if len(t_list)>2 else t_list[0]}.", "marks_category": 10, "frequency": "Medium"}
                ]
            }
            db_adapter.save_unit(unit_doc)

    # Question Paper Mapping for Deep Learning IA1, IA2, IA3
    qp_dl_ia1 = {
        "subject": "Deep Learning",
        "exam_name": "Internal Assessment 1",
        "unit_number": 1,
        "questions": [
            {"question_id": "Q1", "topic": "Perceptron Model", "max_marks": 5, "unit_number": 1},
            {"question_id": "Q2", "topic": "Activation Functions", "max_marks": 5, "unit_number": 1},
            {"question_id": "Q3", "topic": "Gradient Descent", "max_marks": 10, "unit_number": 1},
            {"question_id": "Q4", "topic": "Multilayer Perceptron (MLP)", "max_marks": 10, "unit_number": 1}
        ]
    }

    qp_dl_ia2 = {
        "subject": "Deep Learning",
        "exam_name": "Internal Assessment 2",
        "unit_number": 2,
        "questions": [
            {"question_id": "Q1", "topic": "CNN Architecture", "max_marks": 5, "unit_number": 2},
            {"question_id": "Q2", "topic": "Convolution & Pooling", "max_marks": 5, "unit_number": 2},
            {"question_id": "Q3", "topic": "ResNet & Skip Connections", "max_marks": 10, "unit_number": 2}
        ]
    }

    qp_dl_ia3 = {
        "subject": "Deep Learning",
        "exam_name": "Internal Assessment 3",
        "unit_number": 3,
        "questions": [
            {"question_id": "Q1", "topic": "RNN Architecture", "max_marks": 5, "unit_number": 3},
            {"question_id": "Q2", "topic": "LSTM Networks", "max_marks": 10, "unit_number": 3},
            {"question_id": "Q3", "topic": "GRU Gated Units", "max_marks": 10, "unit_number": 3}
        ]
    }

    db_adapter.save_question_paper(qp_dl_ia1)
    db_adapter.save_question_paper(qp_dl_ia2)
    db_adapter.save_question_paper(qp_dl_ia3)

    # Student Marks (STU101 & STU102)
    marks_stu101_ia1 = {
        "subject": "Deep Learning",
        "exam_name": "Internal Assessment 1",
        "student_id": "STU101",
        "student_name": "John Doe",
        "question_scores": {"Q1": 5, "Q2": 3, "Q3": 2, "Q4": 8}
    }
    marks_stu101_ia2 = {
        "subject": "Deep Learning",
        "exam_name": "Internal Assessment 2",
        "student_id": "STU101",
        "student_name": "John Doe",
        "question_scores": {"Q1": 4, "Q2": 4, "Q3": 7}
    }
    marks_stu101_ia3 = {
        "subject": "Deep Learning",
        "exam_name": "Internal Assessment 3",
        "student_id": "STU101",
        "student_name": "John Doe",
        "question_scores": {"Q1": 4, "Q2": 9, "Q3": 8}
    }

    db_adapter.save_student_marks(marks_stu101_ia1)
    db_adapter.save_student_marks(marks_stu101_ia2)
    db_adapter.save_student_marks(marks_stu101_ia3)

    print("[Seed Engine] Seeding complete! Database pre-loaded with 5 Units for all subjects.")

if __name__ == "__main__":
    seed_database()
