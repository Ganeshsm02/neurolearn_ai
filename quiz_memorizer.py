# -*- coding: utf-8 -*-
"""
Deep Learning & Generative AI Interactive Memorizer & Quiz Terminal App
----------------------------------------------------------------------
Covers:
- Deep Learning (Units 1 - 5)
- Generative AI & LLMs (Units 1 - 5)
"""

import os
import sys
import random
import time

# Terminal Colors for aesthetic CLI
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Comprehensive Quiz Database covering all syllabus topics
QUESTION_BANK = [
    # =========================================================================
    # DEEP LEARNING - UNIT 1
    # =========================================================================
    {
        "subject": "Deep Learning",
        "unit": 1,
        "topic": "Introduction to Neural Network & Feed Forward Nets",
        "question": "In a standard Feed-Forward Neural Network (FFNN), how do signals flow during forward propagation?",
        "options": [
            "Signals flow strictly forward from input to output with no cycles or feedback loops.",
            "Signals loop backwards continuously during forward propagation.",
            "Nodes connect strictly to nodes in the same layer only.",
            "Signals skip activation functions and operate as linear combinations only."
        ],
        "answer": 0,
        "explanation": "Feed-Forward Neural Networks process information sequentially from the input layer through hidden layers to the output layer without feedback loops during forward propagation.",
        "memory_tip": "Feed-Forward = 'One-way street' from Input -> Hidden -> Output."
    },
    {
        "subject": "Deep Learning",
        "unit": 1,
        "topic": "TensorFlow & DL Fundamentals",
        "question": "Which component in TensorFlow automates the calculation of gradients during backpropagation?",
        "options": [
            "tf.data.Dataset",
            "tf.GradientTape",
            "tf.keras.layers.Dense",
            "tf.estimator"
        ],
        "answer": 1,
        "explanation": "tf.GradientTape records operations executed inside its context to perform automatic differentiation (autograd).",
        "memory_tip": "Tape 'records' forward math so TensorFlow can retrace & compute derivatives backward."
    },
    {
        "subject": "Deep Learning",
        "unit": 1,
        "topic": "Deep Learning Algorithms & Types",
        "question": "Why is the ReLU (Rectified Linear Unit) activation function preferred over Sigmoid in deep networks?",
        "options": [
            "ReLU outputs values bounded strictly between -1 and 1.",
            "ReLU mitigates the vanishing gradient problem for positive inputs by maintaining a constant gradient of 1.",
            "ReLU is differentiable at exactly zero.",
            "Sigmoid requires significantly less computation than ReLU."
        ],
        "answer": 1,
        "explanation": "Sigmoid saturates at 0 and 1 (causing vanishing gradients in deep networks), whereas ReLU f(x) = max(0, x) has derivative 1 for x > 0.",
        "memory_tip": "ReLU keeps gradients alive for x > 0 (Derivative = 1)."
    },

    # =========================================================================
    # DEEP LEARNING - UNIT 2
    # =========================================================================
    {
        "subject": "Deep Learning",
        "unit": 2,
        "topic": "CNN Filters, Strides, and Padding",
        "question": "Given an input image of size 32x32, filter size 5x5, stride 1, and padding 'SAME', what will be the spatial dimensions of the output feature map?",
        "options": [
            "28x28",
            "30x30",
            "32x32",
            "36x36"
        ],
        "answer": 2,
        "explanation": "With 'SAME' padding and stride 1, the output spatial dimensions match the input spatial dimensions exactly (32x32).",
        "memory_tip": "'SAME' padding preserves dimensions when Stride = 1."
    },
    {
        "subject": "Deep Learning",
        "unit": 2,
        "topic": "Improving CNN Performance & Advanced Computer Vision",
        "question": "Which technique randomly deactivates a fraction of neurons during training to prevent co-adaptation and overfitting in CNNs?",
        "options": [
            "Batch Normalization",
            "Dropout",
            "Data Augmentation",
            "Residual Connections"
        ],
        "answer": 1,
        "explanation": "Dropout randomly sets output features of hidden units to zero during training with probability p, reducing overfitting.",
        "memory_tip": "Dropout = 'Dropping out' random neurons to prevent over-reliance."
    },
    {
        "subject": "Deep Learning",
        "unit": 2,
        "topic": "Structure of CNNs & Multilevel Convolution",
        "question": "What primary advantage do 1x1 convolutions (pointwise convolutions) provide in architectures like Inception and ResNet?",
        "options": [
            "They increase the spatial dimensions of feature maps.",
            "They perform spatial smoothing across pixels.",
            "They reduce channel dimensionality (channel compression) with low computational cost.",
            "They replace pooling layers completely."
        ],
        "answer": 2,
        "explanation": "1x1 convolutions linearly combine feature maps across the channel dimension, enabling dimensionality reduction (bottlenecking) before expensive 3x3 or 5x5 filters.",
        "memory_tip": "1x1 convs reduce CHANNELS (depth), not width or height!"
    },

    # =========================================================================
    # DEEP LEARNING - UNIT 3
    # =========================================================================
    {
        "subject": "Deep Learning",
        "unit": 3,
        "topic": "RNNs & Bidirectional / Deep RNNs",
        "question": "Why do standard Recurrent Neural Networks (RNNs) struggle with long-range dependencies?",
        "options": [
            "They lack non-linear activation functions.",
            "Repeated matrix multiplication during backpropagation through time causes gradients to explode or vanish.",
            "They can only process one word per epoch.",
            "Bidirectional passes overwrite internal memory state."
        ],
        "answer": 1,
        "explanation": "Backpropagation Through Time (BPTT) involves multiplying weight matrices across many timesteps, driving gradients exponentially to 0 (vanishing) or infinity (exploding).",
        "memory_tip": "BPTT chain rule = repeated multiplication -> vanishing/exploding gradients."
    },
    {
        "subject": "Deep Learning",
        "unit": 3,
        "topic": "Autoencoders (Complete, Regularized, Stochastic, Contractive)",
        "question": "What is the primary constraint introduced by a Contractive Autoencoder during training?",
        "options": [
            "It forces encoder weights to be binary (0 or 1).",
            "It penalizes the Frobenius norm of the Jacobian matrix of the encoder activations with respect to the input.",
            "It adds random Gaussian noise to the input layer.",
            "It uses a decoder with fixed, non-trainable weights."
        ],
        "answer": 1,
        "explanation": "Contractive Autoencoders add a Frobenius norm penalty on the Jacobian matrix of hidden representations to make learned representations robust against small perturbations in inputs.",
        "memory_tip": "Contractive = Jacobian Penalty (resists small input perturbations)."
    },
    {
        "subject": "Deep Learning",
        "unit": 3,
        "topic": "Seq2Seq Learning & Language Modelling",
        "question": "In a Sequence-to-Sequence (Seq2Seq) architecture using Encoder-Decoder LSTM, how is information transferred from encoder to decoder?",
        "options": [
            "Through a continuous gradient stream without a hidden state.",
            "Via the final hidden/cell state of the Encoder, acting as a summary context vector.",
            "By feeding target tokens directly into the Encoder input.",
            "By taking the average of all embedding tables."
        ],
        "answer": 1,
        "explanation": "In basic Seq2Seq, the final hidden state of the encoder compresses the entire input sequence into a fixed-length context vector passed to start the decoder.",
        "memory_tip": "Seq2Seq Bottleneck = Final Encoder State -> Context Vector -> Decoder."
    },

    # =========================================================================
    # DEEP LEARNING - UNIT 4
    # =========================================================================
    {
        "subject": "Deep Learning",
        "unit": 4,
        "topic": "Reinforcement Learning Theory & MDP",
        "question": "A Markov Decision Process (MDP) is formally defined by which tuple of components?",
        "options": [
            "(States, Actions, Transition Probabilities, Rewards, Discount Factor gamma)",
            "(Nodes, Edges, Weights, Biases, Activation Functions)",
            "(Environment, Agent, Loss Function, Optimizer, Learning Rate)",
            "(Observations, Predictions, Targets, Errors, Gradients)"
        ],
        "answer": 0,
        "explanation": "An MDP is represented by (S, A, P, R, γ), where S is state space, A is action space, P is transition probability, R is reward function, and γ is discount factor.",
        "memory_tip": "MDP = (S, A, P, R, γ)"
    },
    {
        "subject": "Deep Learning",
        "unit": 4,
        "topic": "Q-Learning & Deep Q-Learning (DQN)",
        "question": "What key innovation introduced in Deep Q-Networks (DQN) stabilizes learning when using neural networks as function approximators?",
        "options": [
            "Policy Gradient Theorem and Monte Carlo rollouts",
            "Experience Replay Buffer and Target Network",
            "Softmax action selection without exploration",
            "State-action value table hashing"
        ],
        "answer": 1,
        "explanation": "DQN uses Experience Replay (breaking temporal correlation in data batches) and a separate Target Network (updated periodically to stabilize TD targets).",
        "memory_tip": "DQN stability = Experience Replay + Target Network!"
    },
    {
        "subject": "Deep Learning",
        "unit": 4,
        "topic": "Policy Gradient & Actor-Critic Methods",
        "question": "In an Actor-Critic architecture, what are the respective roles of the 'Actor' and the 'Critic'?",
        "options": [
            "The Actor calculates loss; the Critic updates network weights.",
            "The Actor learns the policy (selects actions); the Critic evaluates state/action values (provides baseline/advantage).",
            "The Actor explores randomly; the Critic executes greedy actions.",
            "The Actor handles image processing; the Critic handles vector memory."
        ],
        "answer": 1,
        "explanation": "The Actor updates policy parameters pi(a|s), while the Critic estimates the value function V(s) or Q(s,a) to evaluate the action taken and reduce variance.",
        "memory_tip": "Actor = Policy (Action chooser), Critic = Value evaluator (Feedback giver)."
    },

    # =========================================================================
    # DEEP LEARNING - UNIT 5
    # =========================================================================
    {
        "subject": "Deep Learning",
        "unit": 5,
        "topic": "Autonomous Vehicles & ChauffeurNet",
        "question": "What type of learning methodology does ChauffeurNet rely on for autonomous driving policy generation?",
        "options": [
            "Pure Unsupervised Clustering",
            "Imitation Learning (Behavioral Cloning) augmented with synthesized perturbation trajectories",
            "Tabular Q-learning",
            "Genetic Evolutionary Strategies"
        ],
        "answer": 1,
        "explanation": "ChauffeurNet uses imitation learning from human expert demonstrations while synthesizing perturbed synthetic trajectories to handle out-of-distribution collision scenes.",
        "memory_tip": "ChauffeurNet = Imitation Learning + Synthetic Noise/Perturbations."
    },

    # =========================================================================
    # GENERATIVE AI & LLM - UNIT 1
    # =========================================================================
    {
        "subject": "Generative AI and LLM",
        "unit": 1,
        "topic": "Introduction to GenAI & Foundation Models",
        "question": "What fundamentally distinguishes Generative AI models from Discriminative AI models?",
        "options": [
            "Discriminative models learn P(X, Y), whereas Generative models learn P(Y|X).",
            "Generative models learn joint probability distribution P(X, Y) or data distribution P(X) to produce new data, whereas Discriminative models learn conditional distribution P(Y|X) to classify.",
            "Generative models can only process text, while discriminative models process vision.",
            "Discriminative models require neural networks, while generative models do not."
        ],
        "answer": 1,
        "explanation": "Generative models model data generation distribution P(X) or P(X|Y) to generate new instances, while discriminative models estimate class boundaries P(Y|X).",
        "memory_tip": "Generative = Learns how data is created (P(X)). Discriminative = Learns boundary (P(Y|X))."
    },
    {
        "subject": "Generative AI and LLM",
        "unit": 1,
        "topic": "Pre-trained Models & Transfer Learning",
        "question": "What is the primary benefit of pre-training a Foundation Model on massive unlabeled datasets before downstream task adaptation?",
        "options": [
            "Eliminates the need for GPU computation completely.",
            "Enables the model to learn rich, generalized domain representations that transfer efficiently to specialized tasks with minimal downstream data.",
            "Guarantees 100% accuracy on non-text tasks.",
            "Ensures model parameters remain completely frozen forever."
        ],
        "answer": 1,
        "explanation": "Pre-training extracts structural language/visual priors from vast corpora, enabling high performance on downstream tasks via fine-tuning or prompt tuning.",
        "memory_tip": "Pre-training = Broad general knowledge; Transfer learning = Specialized application."
    },

    # =========================================================================
    # GENERATIVE AI & LLM - UNIT 2
    # =========================================================================
    {
        "subject": "Generative AI and LLM",
        "unit": 2,
        "topic": "Transformer Architecture & Self-Attention",
        "question": "In the standard Scaled Dot-Product Attention formula Softmax( (Q * K^T) / sqrt(d_k) ) * V, why is the scaling factor sqrt(d_k) applied?",
        "options": [
            "To prevent dot products from growing excessively large in high dimensions, which would cause softmax gradients to vanish.",
            "To scale down sequence length for faster execution.",
            "To convert non-linear embeddings back into linear vectors.",
            "To enforce causality in decoder self-attention."
        ],
        "answer": 0,
        "explanation": "For large values of key dimension d_k, dot products grow large in magnitude, pushing softmax into regions with extremely small gradients. Dividing by sqrt(d_k) stabilizes gradients.",
        "memory_tip": "Scale by sqrt(d_k) = Prevents large dot products -> Avoids vanishing softmax gradients."
    },
    {
        "subject": "Generative AI and LLM",
        "unit": 2,
        "topic": "BERT, GPT, T5, LLaMA & MoE Architectures",
        "question": "How do Decoder-only LLMs (e.g., GPT, LLaMA) differ structurally from Encoder-only models (e.g., BERT)?",
        "options": [
            "Decoder-only models use causal masking (left-to-right attention) for autoregressive generation, whereas BERT uses bidirectional attention.",
            "BERT generates tokens one by one autoregressively; GPT processes entire sequences in parallel at inference.",
            "LLaMA uses cross-attention layers, while BERT does not.",
            "GPT models do not use positional encodings."
        ],
        "answer": 0,
        "explanation": "Decoder-only models enforce causal masks so token i can only attend to tokens <= i (autoregressive generation), whereas BERT looks at both past and future tokens bidirectionally.",
        "memory_tip": "BERT = Bidirectional Encoder (Classification/Masked). GPT = Causal Decoder (Autoregressive Text Gen)."
    },
    {
        "subject": "Generative AI and LLM",
        "unit": 2,
        "topic": "Mixture of Experts (MoE) & Scaling Laws",
        "question": "What is the key computational advantage of a Mixture of Experts (MoE) architecture like Mixtral or Switch Transformer?",
        "options": [
            "It routes tokens through a sparse subset of expert feedforward networks, maintaining huge total parameters with low FLOPs per token.",
            "It replaces matrix multiplication with simple additions.",
            "It eliminates attention layers completely.",
            "It compresses context window to under 128 tokens."
        ],
        "answer": 0,
        "explanation": "MoE uses a router to dynamically select only 1 or 2 top experts per token, allowing massive parameter scaling without proportional inference compute scaling.",
        "memory_tip": "MoE = High total params + Sparse token routing = Fast inference!"
    },

    # =========================================================================
    # GENERATIVE AI & LLM - UNIT 3
    # =========================================================================
    {
        "subject": "Generative AI and LLM",
        "unit": 3,
        "topic": "VAEs, GANs, and Diffusion Models",
        "question": "How do Diffusion Models synthesize realistic images compared to GANs?",
        "options": [
            "By playing a zero-sum game between a Generator and Discriminator.",
            "By learning a reverse denoising process that iteratively removes Gaussian noise from a random noise tensor over multiple steps.",
            "By passing input images through a discrete VQ-VAE codebook in one step.",
            "By computing exact maximum likelihood via linear regression."
        ],
        "answer": 1,
        "explanation": "Diffusion models define a forward process adding noise to data, and train a neural net (U-Net) to reverse this process step-by-step from pure noise to clean images.",
        "memory_tip": "Diffusion = Forward Noise Addition -> Reverse Iterative Denoising."
    },
    {
        "subject": "Generative AI and LLM",
        "unit": 3,
        "topic": "Multimodal AI Systems",
        "question": "In multimodal models like CLIP (Contrastive Language-Image Pre-training), how are text and image modalities aligned?",
        "options": [
            "By translating text into pixel matrices.",
            "By joint contrastive learning that maximizes cosine similarity of matching (image, text) pairs while minimizing non-matching pairs in a shared embedding space.",
            "By feeding raw image bytes directly into a transformer decoder token pipeline.",
            "By using Speech-to-Text as an intermediate representation."
        ],
        "answer": 1,
        "explanation": "CLIP trains an image encoder and text encoder simultaneously using contrastive loss to map correlated images and text prompts into a shared high-dimensional latent space.",
        "memory_tip": "CLIP = Shared Latent Space + Contrastive Pair Matching."
    },

    # =========================================================================
    # GENERATIVE AI & LLM - UNIT 4
    # =========================================================================
    {
        "subject": "Generative AI and LLM",
        "unit": 4,
        "topic": "Prompt Engineering & RAG",
        "question": "What is the primary architecture flow of a Retrieval-Augmented Generation (RAG) system?",
        "options": [
            "Prompt -> Fine-tuning weights -> Direct LLM output",
            "User Query -> Vector Embedding -> Vector DB similarity search -> Retrieve Relevant Context -> Augmented Prompt -> LLM Generation",
            "User Query -> Image Classifier -> Diffusion Denoising -> Audio Output",
            "User Query -> Tokenizer -> Softmax -> Greedy Search"
        ],
        "answer": 1,
        "explanation": "RAG enhances LLM responses by retrieving relevant grounding documents from a vector database using semantic similarity search before generating the response.",
        "memory_tip": "RAG = Search Vector DB -> Inject Context into Prompt -> Ask LLM."
    },
    {
        "subject": "Generative AI and LLM",
        "unit": 4,
        "topic": "Instruction Tuning & RLHF",
        "question": "What is the role of the Reward Model in Reinforcement Learning from Human Feedback (RLHF)?",
        "options": [
            "It generates initial draft responses.",
            "It scores candidate responses based on human preference alignments to guide Policy Optimization (PPO).",
            "It truncates context windows to stay within token limits.",
            "It calculates BLEU and ROUGE scores automatically."
        ],
        "answer": 1,
        "explanation": "In RLHF, human rankings train a Reward Model to output scalar scores reflecting helpfulness and safety. PPO uses this scalar reward to update the LLM policy.",
        "memory_tip": "RLHF: Human Rankings -> Reward Model -> PPO Policy Update."
    },

    # =========================================================================
    # GENERATIVE AI & LLM - UNIT 5
    # =========================================================================
    {
        "subject": "Generative AI and LLM",
        "unit": 5,
        "topic": "Autonomous Agents & AI Safety / Responsible AI",
        "question": "What pattern enables Autonomous AI Agents to solve complex multi-step tasks by iterative planning, action execution, and observation?",
        "options": [
            "ReAct (Reason + Act) framework",
            "Greedy Beam Search decoding",
            "Zero-shot classification",
            "Contrastive loss fine-tuning"
        ],
        "answer": 0,
        "explanation": "The ReAct (Reasoning and Acting) paradigm prompts agents to interleave thought reasoning steps with tool execution actions and observations to accomplish complex tasks.",
        "memory_tip": "ReAct Agent = Thought (Reason) -> Action (Tool) -> Observation."
    },
    {
        "subject": "Generative AI and LLM",
        "unit": 5,
        "topic": "Adversarial Attacks & AI Safety",
        "question": "What type of attack involves crafting prompts to bypass system guardrails, safety filters, or system instructions?",
        "options": [
            "Jailbreaking / Prompt Injection",
            "Data Drift",
            "Catastrophic Forgetting",
            "Vanishing Gradient Attack"
        ],
        "answer": 0,
        "explanation": "Jailbreaking and Prompt Injection manipulate LLM context inputs to override safety policies or trigger unauthorized actions.",
        "memory_tip": "Prompt Injection / Jailbreak = Bypassing safety rules via malicious input."
    }
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(f"{Colors.HEADER}{Colors.BOLD}===================================================================={Colors.ENDC}")
    print(f"{Colors.OKCYAN}{Colors.BOLD}   🧠 DEEP LEARNING & GENERATIVE AI / LLM MEMORIZER & QUIZ SYSTEM    {Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}===================================================================={Colors.ENDC}\n")

def run_unit_quiz(subject_filter=None, unit_filter=None):
    print_header()
    filtered_q = QUESTION_BANK
    if subject_filter:
        filtered_q = [q for q in filtered_q if q["subject"] == subject_filter]
    if unit_filter:
        filtered_q = [q for q in filtered_q if q["unit"] == unit_filter]
        
    if not filtered_q:
        print(f"{Colors.WARNING}No questions found for the selected filter.{Colors.ENDC}")
        input("\nPress Enter to return to main menu...")
        return

    score = 0
    total = len(filtered_q)
    questions = list(filtered_q)
    random.shuffle(questions)

    print(f"{Colors.BOLD}Starting Quiz ({total} Questions){Colors.ENDC}\n" + "-"*50)

    for idx, q in enumerate(questions, start=1):
        print(f"\n{Colors.OKBLUE}[Question {idx}/{total}] [{q['subject']} - Unit {q['unit']}: {q['topic']}]{Colors.ENDC}")
        print(f"{Colors.BOLD}{q['question']}{Colors.ENDC}\n")
        
        for i, opt in enumerate(q['options']):
            print(f"  {Colors.OKCYAN}{i + 1}.{Colors.ENDC} {opt}")
            
        ans = input(f"\n{Colors.BOLD}Your answer (1-{len(q['options'])}): {Colors.ENDC}").strip()
        
        try:
            ans_idx = int(ans) - 1
            if ans_idx == q['answer']:
                print(f"\n{Colors.OKGREEN}✓ CORRECT!{Colors.ENDC}")
                score += 1
            else:
                correct_letter = q['options'][q['answer']]
                print(f"\n{Colors.FAIL}✗ INCORRECT!{Colors.ENDC} Correct answer: {Colors.BOLD}{correct_letter}{Colors.ENDC}")
        except ValueError:
            print(f"\n{Colors.FAIL}Invalid input! Counted as incorrect.{Colors.ENDC}")

        print(f"{Colors.WARNING}💡 Explanation:{Colors.ENDC} {q['explanation']}")
        print(f"{Colors.HEADER}📌 Memory Hook:{Colors.ENDC} {q['memory_tip']}")
        print("-" * 50)
        time.sleep(0.5)

    pct = (score / total) * 100
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== QUIZ RESULTS ==={Colors.ENDC}")
    print(f"Score: {Colors.BOLD}{score} / {total}{Colors.ENDC} ({pct:.1f}%)")
    if pct >= 80:
        print(f"{Colors.OKGREEN}🌟 Outstanding! You have mastered these topics!{Colors.ENDC}")
    elif pct >= 60:
        print(f"{Colors.WARNING}👍 Good effort! Review the memory hooks to reach 100%.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}📚 Keep practicing! Use Flashcard Mode for active recall.{Colors.ENDC}")
    
    input("\nPress Enter to return to main menu...")

def run_flashcards():
    print_header()
    print(f"{Colors.BOLD}⚡ FLASHCARD & ACTIVE RECALL MEMORIZATION MODE ⚡{Colors.ENDC}")
    print("Read the topic and question, recall the answer in your mind, then reveal!\n" + "="*60)
    
    questions = list(QUESTION_BANK)
    random.shuffle(questions)
    
    for idx, q in enumerate(questions, start=1):
        print(f"\n{Colors.OKBLUE}Flashcard {idx}/{len(questions)}: [{q['subject']} - Unit {q['unit']}: {q['topic']}]{Colors.ENDC}")
        print(f"{Colors.BOLD}Q: {q['question']}{Colors.ENDC}\n")
        
        input(f"{Colors.WARNING}Press Enter to reveal answer & memory tip...{Colors.ENDC}")
        
        correct_opt = q['options'][q['answer']]
        print(f"\n{Colors.OKGREEN}Answer: {correct_opt}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Explanation: {q['explanation']}{Colors.ENDC}")
        print(f"{Colors.HEADER}💡 Memory Hook: {q['memory_tip']}{Colors.ENDC}")
        print("-" * 60)
        
        cont = input("\nContinue to next flashcard? (y/n): ").strip().lower()
        if cont == 'n':
            break

def display_cheat_sheet():
    print_header()
    print(f"{Colors.BOLD}📖 COMPLETE SYLLABUS MEMORIZATION CHEAT SHEET 📖{Colors.ENDC}\n")
    
    units_map = {}
    for q in QUESTION_BANK:
        key = f"{q['subject']} - Unit {q['unit']}"
        if key not in units_map:
            units_map[key] = []
        units_map[key].append(q)
        
    for u_key, items in units_map.items():
        print(f"{Colors.HEADER}{Colors.BOLD}=== {u_key} ==={Colors.ENDC}")
        for item in items:
            print(f"  • {Colors.BOLD}{item['topic']}{Colors.ENDC}")
            print(f"    - {Colors.OKCYAN}Key Concept:{Colors.ENDC} {item['explanation']}")
            print(f"    - {Colors.WARNING}Memory Hook:{Colors.ENDC} {item['memory_tip']}\n")
            
    input("\nPress Enter to return to main menu...")

def main_menu():
    while True:
        print_header()
        print(f"{Colors.BOLD}Select Learning / Memorization Mode:{Colors.ENDC}\n")
        print(f"  {Colors.OKCYAN}1.{Colors.ENDC} Run Full Comprehensive Exam (All 10 Units)")
        print(f"  {Colors.OKCYAN}2.{Colors.ENDC} Deep Learning Quiz (Units 1 - 5)")
        print(f"  {Colors.OKCYAN}3.{Colors.ENDC} Generative AI & LLM Quiz (Units 1 - 5)")
        print(f"  {Colors.OKCYAN}4.{Colors.ENDC} Flashcard Active Recall Mode")
        print(f"  {Colors.OKCYAN}5.{Colors.ENDC} View Complete Memorization Cheat Sheet")
        print(f"  {Colors.OKCYAN}6.{Colors.ENDC} Exit")
        
        choice = input(f"\n{Colors.BOLD}Enter choice (1-6): {Colors.ENDC}").strip()
        
        if choice == '1':
            run_unit_quiz()
        elif choice == '2':
            run_unit_quiz(subject_filter="Deep Learning")
        elif choice == '3':
            run_unit_quiz(subject_filter="Generative AI and LLM")
        elif choice == '4':
            run_flashcards()
        elif choice == '5':
            display_cheat_sheet()
        elif choice == '6':
            print(f"\n{Colors.OKGREEN}Happy Learning & Good Luck! Goodbye!{Colors.ENDC}")
            sys.exit(0)
        else:
            print(f"{Colors.FAIL}Invalid choice. Please select 1-6.{Colors.ENDC}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Program exited by user.{Colors.ENDC}")
        sys.exit(0)
