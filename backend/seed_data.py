import os
import sys

# Ensure backend directory is on Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_adapter

def seed_database():
    print("[Seed Engine] Seeding all 5 Units for Deep Learning & Generative AI / LLMs into NeuroLearn AI...")

    subjects = [
        "Deep Learning",
        "Generative AI and LLM",
        "Machine Learning",
        "MLOps",
        "Cloud Computing & Application Development (CCAD)"
    ]

    unit_titles = {
        "Deep Learning": {
            1: "Introduction to Neural Networks, Feed Forward Nets & TensorFlow",
            2: "Convolutional Neural Networks (CNNs) & Advanced Computer Vision",
            3: "Recurrent Neural Networks, Autoencoders & Sequence Learning",
            4: "Reinforcement Learning Theory, Q-Learning & Actor-Critic",
            5: "Autonomous Vehicles & DL in Cloud"
        },
        "Generative AI and LLM": {
            1: "Introduction to Generative AI & Foundation Model Ecosystems",
            2: "Sequence Modelling, Transformers, Self-Attention & LLM Architectures",
            3: "Probabilistic Generative Models, VAEs, GANs, Diffusion & Multimodal AI",
            4: "Prompt Engineering, Instruction Tuning, RLHF & RAG Systems",
            5: "Applications, Autonomous Agents, APIs, Cloud & Responsible AI"
        }
    }

    topics_pool = {
        "Deep Learning": {
            1: ["Introduction to Neural Network", "Feed Forward Neural Nets", "Tensorflow", "Deep Learning Fundamentals", "Deep Learning Algorithms and Types"],
            2: ["Convolutional Neural Networks", "Filters", "Strides and Padding", "Structure of Convolutional Network", "Improving Performance of CNNs", "Multilevel Convolution", "Computer Vision with CNNs", "Advanced Computer Vision"],
            3: ["Recurrent Neural Networks", "Recursive Neural Networks", "Bidirectional RNNs", "Deep Recurrent Networks", "Complete & Regularized Autoencoders", "Stochastic & Contractive Encoders", "Language Modelling", "Sequence to Sequence Learning", "Speech Recognition"],
            4: ["Reinforcement Learning Theory", "Markov Decision Process", "Monte Carlo Methods", "Temporal Difference Methods", "Value Functions", "Q Learning", "Deep Q-Learning", "Policy Gradient Methods", "Model-Based Methods", "Actor-Critic Methods"],
            5: ["Autonomous Vehicles Introduction", "Imitation Driving Policy", "Driving Policy with ChauffeurNet", "DL in Cloud"]
        },
        "Generative AI and LLM": {
            1: ["Introduction to Generative AI", "Evolution of Generative Models", "Types of Generative AI", "Foundation Models & LLMs", "Pre-trained Models & Transfer Learning", "Applications of Generative AI", "Foundation Model Ecosystems & Platforms"],
            2: ["Sequence Modelling", "Transformer Architecture", "Self-Attention & Multi-head Attention", "Positional Encoding", "Encoder and Decoder Models", "BERT, GPT, T5, LLaMA Architectures", "Tokenization Techniques", "Embeddings & Vector Representations", "Scaling Laws in LLMs", "Mixture of Experts (MoE)", "Emergent Capabilities"],
            3: ["Generative Models as Probabilistic Models", "Representation Learning & Latent Space", "Autoencoders & Variational Autoencoders (VAE)", "Generative Adversarial Networks (GANs)", "Diffusion Models & Image Synthesis", "Comparative Analysis of Architectures", "Evolution of Multimodal AI Systems", "Text, Image & Audio Understanding", "Emerging Multimodal Foundation Models"],
            4: ["Prompt Engineering Fundamentals", "Zero-shot, One-shot & Few-shot Prompting", "Chain of Thought Prompting", "Instruction Tuning", "Fine-Tuning & Transfer Learning", "RLHF", "Retrieval Augmented Generation (RAG)", "Vector Databases", "Context Management", "Evaluation Metrics for LLMs", "Hallucination & Bias Reduction"],
            5: ["Text Generation & Summarization", "Conversational AI & Chatbots", "AI Code Generation", "Image Generation Models", "Diffusion Models & GANs", "Speech & Audio Generation", "AI Assistants & Autonomous Agents", "Multimodal AI Systems", "Generative AI APIs & Frameworks", "Cloud-based AI Deployment", "Real-time Generative AI Applications", "AI Bias & Fairness", "Privacy & Security Considerations", "Adversarial Attacks & AI Safety", "Responsible Use of Generative AI Systems"]
        }
    }

    for sub in subjects:
        sub_topics = topics_pool.get(sub, {})
        sub_unit_titles = unit_titles.get(sub, {})
        for u_num in range(1, 6):
            t_list = sub_topics.get(u_num, [
                f"{sub} Unit {u_num} Fundamentals",
                f"{sub} Unit {u_num} Core Theory",
                f"{sub} Unit {u_num} Optimization",
                f"{sub} Unit {u_num} Applications"
            ])
            u_title = sub_unit_titles.get(u_num, f"Unit {u_num}: {sub} Advanced Concepts")

            unit_doc = {
                "subject": sub,
                "unit_number": u_num,
                "unit_title": f"Unit {u_num}: {u_title}",
                "topics": t_list,
                "subtopics": [f"Overview of {t}" for t in t_list],
                "key_concepts": [
                    {"name": t_list[0], "description": f"Core theoretical principle for {t_list[0]}."},
                    {"name": t_list[1] if len(t_list)>1 else t_list[0], "description": f"Practical application guide for {t_list[1] if len(t_list)>1 else t_list[0]}."}
                ],
                "important_questions": [
                    {"question": f"Explain the core mechanisms, equations, and applications of {t_list[0]}.", "marks_category": 10, "frequency": "High"},
                    {"question": f"Compare and contrast {t_list[0]} with {t_list[1] if len(t_list)>1 else t_list[0]}.", "marks_category": 5, "frequency": "High"},
                    {"question": f"Discuss key challenges and optimization strategies in {t_list[2] if len(t_list)>2 else t_list[0]}.", "marks_category": 10, "frequency": "Medium"}
                ]
            }
            db_adapter.save_unit(unit_doc)

    print("[Seed Engine] Seeding complete! Pre-loaded all 5 Units for Deep Learning & Generative AI / LLM.")

if __name__ == "__main__":
    seed_database()
