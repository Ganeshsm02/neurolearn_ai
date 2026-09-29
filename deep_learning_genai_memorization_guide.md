# 🧠 Comprehensive Deep Learning & Generative AI Memorization Guide

> **All-In-One Study Matrix & Active Recall Question Bank**
> *Covering Deep Learning (Units 1–5) and Generative AI & LLMs (Units 1–5)*

---

## 💻 How to Run the Interactive Terminal Quiz App

To start the interactive quiz, flashcard recall, and memorization drills directly in your terminal, run the following command from your project directory:

```powershell
python quiz_memorizer.py
```

*Note: You can also specify the target working directory if running from outside the project directory:*
```powershell
python C:\Users\MOOSA\OneDrive\Documents\clg_projects\mlops\quiz_memorizer.py
```

---

## 📚 SUBJECT 1: DEEP LEARNING

### 🔹 Unit 1: Introduction to Neural Networks & Deep Learning Fundamentals
- **Core Concepts:**
  - **Feed-Forward Neural Networks (FFNN):** Information flows strictly unidirectionally from input layer through hidden layers to output layer.
  - **Activation Functions:** 
    - $\text{Sigmoid}(x) = \frac{1}{1 + e^{-x}}$ (Saturates, prone to vanishing gradients).
    - $\text{ReLU}(x) = \max(0, x)$ (Gradient is 1 for $x > 0$, avoids vanishing gradient).
  - **TensorFlow Autograd (`tf.GradientTape`):** Records operations inside context to compute automatic differentiation during backpropagation.
- **Key Memorization Hook:**
  > 💡 *FFNN = One-way street; ReLU = Gradient 1 for positive inputs; GradientTape = Automatic recorder for derivatives.*

#### ❓ Unit 1 Practice Questions:
1. **Q:** What is the primary cause of the vanishing gradient problem in deep FFNNs using Sigmoid activations?
   - **A:** Sigmoid derivatives saturate near 0 for high magnitude inputs, causing gradient updates to shrink exponentially as they backpropagate.
2. **Q:** How does TensorFlow track operations for automatic differentiation?
   - **A:** Using `tf.GradientTape()` context manager.

---

### 🔹 Unit 2: Convolutional Neural Networks (CNNs) & Computer Vision
- **Core Concepts:**
  - **Spatial Dimensions Formula:**
    $$O = \left\lfloor \frac{W - F + 2P}{S} \right\rfloor + 1$$
    *(where $W$ = Input width, $F$ = Filter size, $P$ = Padding, $S$ = Stride).*
  - **Padding Types:** `VALID` (no padding, dimension shrinks), `SAME` (pads so output dimension = input dimension when $S=1$).
  - **1x1 Convolutions (Pointwise Convolutions):** Used for channel-wise dimensionality reduction (bottleneck layers) without altering spatial height/width.
  - **Regularization:** **Dropout** randomly zeroes out neuron activations with probability $p$ during training to prevent co-adaptation.
- **Key Memorization Hook:**
  > 💡 *Output Size = $\frac{W - F + 2P}{S} + 1$; 1x1 Conv = Channel Reducer; Dropout = Prevents Overfitting.*

#### ❓ Unit 2 Practice Questions:
1. **Q:** Given input size 32x32, filter 5x5, stride 1, and padding 'SAME', what is the output size?
   - **A:** 32x32 (SAME padding maintains input dimensions when stride=1).
2. **Q:** What is the function of a 1x1 convolution layer in Inception/ResNet architectures?
   - **A:** Channel dimension compression (reducing computational depth).

---

### 🔹 Unit 3: Recurrent Neural Networks (RNNs) & Sequence Models
- **Core Concepts:**
  - **RNN Limitation:** Backpropagation Through Time (BPTT) leads to vanishing/exploding gradients over long sequences.
  - **Contractive Autoencoder:** Penalizes the Frobenius norm of the encoder's Jacobian matrix with respect to input:
    $$\mathcal{L}_{CAE} = \mathcal{L}(x, g(f(x))) + \lambda \| J_f(x) \|_F^2$$
  - **Seq2Seq Bottleneck:** Standard encoder-decoder networks compress the entire input sequence into a single fixed-length hidden vector.
- **Key Memorization Hook:**
  > 💡 *BPTT = Vanishing gradients; Contractive AE = Jacobian matrix penalty; Seq2Seq = Context vector summary.*

#### ❓ Unit 3 Practice Questions:
1. **Q:** What mathematical penalty does a Contractive Autoencoder enforce?
   - **A:** Frobenius norm penalty on the Jacobian matrix of encoder activations.

---

### 🔹 Unit 4: Reinforcement Learning (RL) Theory & Deep Q-Learning
- **Core Concepts:**
  - **Markov Decision Process (MDP):** Tuple $(S, A, P, R, \gamma)$ defining state, action, transition probability, reward, and discount factor.
  - **Deep Q-Network (DQN) Innovations:**
    1. **Experience Replay Buffer:** Random sampling breaks temporal correlations between consecutive transition tuples.
    2. **Target Network:** Separate network updated periodically to prevent moving target instability in temporal difference loss:
       $$L(\theta) = \mathbb{E}\left[ \left( r + \gamma \max_{a'} Q(s', a'; \theta^-) - Q(s, a; \theta) \right)^2 \right]$$
  - **Actor-Critic:** Actor updates policy $\pi(a|s)$; Critic estimates value $V(s)$ / advantage $A(s,a)$ to reduce variance.
- **Key Memorization Hook:**
  > 💡 *MDP = $(S,A,P,R,\gamma)$; DQN = Replay Buffer + Target Net; Actor = Action Chooser, Critic = Evaluator.*

---

### 🔹 Unit 5: Autonomous Vehicles & DL Applications
- **Core Concepts:**
  - **ChauffeurNet:** Uses Imitation Learning (Behavioral Cloning) augmented with synthetic perturbations (e.g., simulated trajectory errors and collisions) so the agent learns how to recover from dangerous out-of-distribution states.
- **Key Memorization Hook:**
  > 💡 *ChauffeurNet = Imitation Learning + Synthetic Noise/Perturbations.*

---

## 📚 SUBJECT 2: GENERATIVE AI & LARGE LANGUAGE MODELS (LLMs)

### 🔹 Unit 1: Introduction to Generative AI & Foundation Models
- **Core Concepts:**
  - **Generative vs. Discriminative:**
    - Generative models estimate joint probability $P(X, Y)$ or data distribution $P(X)$ to synthesize new samples.
    - Discriminative models estimate conditional probability $P(Y|X)$ to classify inputs.
  - **Foundation Models:** Massively pre-trained models on broad data that can be adapted (transferred) to diverse downstream tasks.
- **Key Memorization Hook:**
  > 💡 *Generative = $P(X)$ (Creates new data); Discriminative = $P(Y|X)$ (Classifies).*

---

### 🔹 Unit 2: Sequence Modelling, Transformer Architecture & Scaling
- **Core Concepts:**
  - **Scaled Dot-Product Attention:**
    $$\text{Attention}(Q, K, V) = \text{Softmax}\left( \frac{Q K^T}{\sqrt{d_k}} \right) V$$
    *Why scale by $\sqrt{d_k}$?* Prevents dot products from growing large in high dimensions, which would cause softmax gradients to vanish.
  - **Architectures:**
    - **BERT (Encoder-only):** Bidirectional masked language model (ideal for embedding, extraction, classification).
    - **GPT / LLaMA (Decoder-only):** Causal (left-to-right) autoregressive language model (ideal for text generation).
    - **T5 (Encoder-Decoder):** Sequence-to-sequence translation and transformation.
  - **Mixture of Experts (MoE):** Routes input tokens to a sparse subset of expert feedforward networks, allowing high parameter counts with low computational FLOPs per token.
- **Key Memorization Hook:**
  > 💡 *Scaling $\sqrt{d_k}$ = Stops gradient vanishing in Softmax; BERT = Bidirectional; GPT = Causal Decoder; MoE = Sparse Routing.*

---

### 🔹 Unit 3: Generative Models (VAEs, GANs, Diffusion & Multimodal)
- **Core Concepts:**
  - **Generative Adversarial Networks (GANs):** Minimax game between Generator $G$ and Discriminator $D$.
  - **Diffusion Models:** Learn a reverse denoising process that gradually removes Gaussian noise step-by-step from $x_T \sim \mathcal{N}(0, I)$ back to clean data $x_0$.
  - **CLIP (Contrastive Language-Image Pre-training):** Jointly trains image and text encoders using contrastive loss to maximize cosine similarity of matching (image, text) pairs in a shared latent space.
- **Key Memorization Hook:**
  > 💡 *GANs = Minimax game; Diffusion = Denoising Gaussian Noise; CLIP = Shared Latent Contrastive Alignment.*

---

### 🔹 Unit 4: Prompt Engineering, Fine-Tuning & RAG
- **Core Concepts:**
  - **Prompting Techniques:** Zero-shot (no examples), Few-shot (in-context examples), Chain-of-Thought (step-by-step reasoning).
  - **Retrieval-Augmented Generation (RAG):**
    `User Query` $\rightarrow$ `Vector Search in Vector DB` $\rightarrow$ `Retrieve Top-K Context` $\rightarrow$ `Augment LLM Prompt` $\rightarrow$ `Grounded Output`.
  - **RLHF (Reinforcement Learning from Human Feedback):**
    Human preference rankings $\rightarrow$ Train Reward Model $\rightarrow$ PPO policy optimization of LLM.
- **Key Memorization Hook:**
  > 💡 *CoT = Step-by-step; RAG = Vector Search + Context Injection; RLHF = Human Rankings -> Reward Model -> PPO.*

---

### 🔹 Unit 5: Autonomous Agents, Applications & AI Safety
- **Core Concepts:**
  - **ReAct Paradigm (Reason + Act):** Interleaves Reasoning ("Thoughts") with Tool Actions ("Actions") and Environment Feedback ("Observations") to execute complex goals.
  - **AI Safety & Adversarial Attacks:**
    - **Jailbreaking / Prompt Injection:** Crafting prompt inputs to bypass safety alignment rules.
    - **Hallucination Mitigation:** Grounding with RAG, citations, and low temperature sampling.
- **Key Memorization Hook:**
  > 💡 *ReAct = Thought -> Action -> Observation; Jailbreak = Prompt injection overriding guardrails.*

---

## 🎯 Quick Self-Assessment Checklist

| Subject | Unit | Primary Topic | Memorized? (Y/N) |
|---|---|---|---|
| Deep Learning | Unit 1 | Feed Forward Nets, ReLU & tf.GradientTape | [ ] |
| Deep Learning | Unit 2 | CNN Padding formula, 1x1 convs & Dropout | [ ] |
| Deep Learning | Unit 3 | BPTT, Contractive Autoencoders & Seq2Seq | [ ] |
| Deep Learning | Unit 4 | MDP Tuple, DQN Replay Buffer & Actor-Critic | [ ] |
| Deep Learning | Unit 5 | ChauffeurNet & Perturbation Trajectories | [ ] |
| GenAI & LLM | Unit 1 | $P(X)$ vs $P(Y\|X)$ & Foundation Models | [ ] |
| GenAI & LLM | Unit 2 | Scaled Attention $\sqrt{d_k}$, BERT vs GPT, MoE | [ ] |
| GenAI & LLM | Unit 3 | Diffusion Denoising, GANs & CLIP Multimodal | [ ] |
| GenAI & LLM | Unit 4 | RAG Pipeline, Chain-of-Thought & RLHF | [ ] |
| GenAI & LLM | Unit 5 | ReAct Agent Framework & Jailbreak Safety | [ ] |
