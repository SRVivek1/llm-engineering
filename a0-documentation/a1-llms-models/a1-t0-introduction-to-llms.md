---
title: "LLM Engineering Session Notes - Architectures, Prompting, and Reasoning"
permalink: ai-ml/llm/_topics/t0-introduction-to-llms.md
layout: course-content
date: 2025-10-31
categories: llm-engineering
tags: [prompt-engineering, rag, fine-tuning, hallucination, risk, markdown]
---

# LLM Engineering Session Notes - Architectures, Prompting, and Reasoning

> * This section covers the core 'breeds' of Large Language Models (LLMs), a key advanced prompting technique, and emerging methods for controlling model reasoning and budgeting. 
> * The target audience is intermediate developers and researchers seeking to deepen their understanding of how modern LLMs are structured and controlled.

## Table of Contents
- [LLM Engineering Session Notes - Architectures, Prompting, and Reasoning](#llm-engineering-session-notes---architectures-prompting-and-reasoning)
  - [Table of Contents](#table-of-contents)
  - [Core LLM Architectures and Breeds](#core-llm-architectures-and-breeds)
    - [1. Base Models](#1-base-models)
    - [2. Chat/Instruct Models](#2-chatinstruct-models)
    - [3. Reasoning/Thinking Models](#3-reasoningthinking-models)
    - [4. Hybrid Models](#4-hybrid-models)
  - [Advanced Prompt Engineering: Chain-of-Thought (CoT)](#advanced-prompt-engineering-chain-of-thought-cot)
    - [The Chain-of-Thought Mechanism](#the-chain-of-thought-mechanism)
  - [Controlling LLM Reasoning and Budget](#controlling-llm-reasoning-and-budget)
    - [Reasoning Models in Practice](#reasoning-models-in-practice)
    - [1. Budget Forcing](#1-budget-forcing)
    - [2. Reinforcing Reasoning with Weighted Keywords](#2-reinforcing-reasoning-with-weighted-keywords)
  - [Key Takeaways](#key-takeaways)

---

## Core LLM Architectures and Breeds

Modern Large Language Models (LLMs) are typically categorized into **three main 'breeds'**, reflecting their primary training objective and intended use case. This distinction is crucial for selecting the right model for a specific engineering task, whether it's raw text completion or complex problem-solving.

### 1\. Base Models

* **Definition:** The initial state of a large language model after the foundational **pre-training** phase on massive datasets (e.g., Common Crawl, Wikipedia).
* **Function:** Its sole purpose is **autoregressive prediction**—taking a sequence of information (input) and predicting the most probable next token (output). It is trained only for next-token prediction, lacking explicit alignment for human instructions or safety.
* **Use Case:** Base models are rarely used directly in production but are the preferred starting point when the goal is to **fine-tune** the model to acquire an entirely new skill or adapt it to a highly specialized, domain-specific task.
* **Alignment Step:** To move from a raw base model (like the original GPT) to a model that follows instructions (like ChatGPT), a process called **Reinforcement Learning from Human Feedback (RLHF)** is often applied. This step aligns the model's output with human preferences.

### 2\. Chat/Instruct Models

* **Definition:** These models are fine-tuned versions of a Base Model, primarily through **Supervised Fine-Tuning (SFT)** and often **RLHF**.
* **Function:** They are explicitly trained to follow instructions and engage in dialogue. They excel at interactive use cases, content generation, summarization, and translation.
* **Key Advantage:** They are generally better at generating **cohesive, conversational responses** and adhering to format constraints provided in a prompt.

### 3\. Reasoning/Thinking Models

* **Definition:** A class of models or a specific mode within a model architecture optimized for complex, multi-step problem-solving.
* **Function:** These models are designed to use an **internal, structured process** to break down a problem, often referred to as a 'thinking' or 'scratchpad' phase, before providing the final answer.
* **Key Advantage:** They are more effective in tasks requiring **logical deduction**, mathematical problem-solving, and managing complex constraints.

### 4\. Hybrid Models

* **Definition:** The latest generation of cutting-edge LLMs that combine the strengths of both Chat/Instruct and Reasoning/Thinking models.
* **Examples:** Models like **Gemini Pro 2.5** and **GPT-5** are examples of this new breed.
* **Function:** They offer **state-of-the-art performance** across a wide spectrum of tasks, capable of both nuanced conversational output and deep, multi-step reasoning.
* **Practical Note:** Open-source projects often release both a pure chat-optimized version and a more robust hybrid version, allowing engineers to select based on specific resource and task needs.

---

## Advanced Prompt Engineering: Chain-of-Thought (CoT)

**Prompt engineering** is the art of crafting inputs to elicit desired, high-quality outputs from an LLM. **Chain-of-Thought (CoT)** prompting is a highly effective, yet simple, technique to significantly improve a model's performance on reasoning-intensive tasks.

### The Chain-of-Thought Mechanism

* 1\. **Core Idea:** By prompting the model to explicitly show its work, you allow it to allocate more internal computational resources to the problem-solving process. This often involves generating an intermediate, *private* reasoning trace.
* 2\. **The Simple CoT Trick:** The most basic and effective application involves appending a simple phrase to your prompt:
    ```markdown
    "Please think step by step."
    ```
    or
    ```markdown
    "Let's break this down before giving the final answer."
    ```
* **Result:** When instructed to use CoT, the model goes through the problem methodically, increasing the likelihood that the predicted sequence of tokens (the final answer) is logically sound and correct.

---

## Controlling LLM Reasoning and Budget

As LLMs become more complex, techniques for managing their internal reasoning processes and the computational **budget** allocated to a query are becoming essential for efficiency and performance.

### Reasoning Models in Practice

When working with models optimized for reasoning, understanding that they operate with an *internal* thought process is key. The **goal of advanced control techniques** is to influence this internal process.

### 1\. Budget Forcing

* **Concept:** This technique involves controlling the **computational resources** (the 'budget') an LLM uses to generate an intermediate reasoning trace. In many advanced architectures, the model might first generate a thought (using a specified number of tokens/compute) before committing to a final answer.
* **Application:** By forcing a minimum or maximum **reasoning budget**, engineers can fine-tune the trade-off between **latency (speed)** and **accuracy (quality)**. A higher budget may improve complex reasoning accuracy but will increase inference time.

### 2\. Reinforcing Reasoning with Weighted Keywords

* **The Discovery (Reported Jan 2025):** Emerging research suggests that it's possible to selectively reinforce the model's internal thinking process by strategically introducing **weighted keywords** into the prompt or, more accurately, into the model's internal processing layers.
* **Mechanism (Conceptual):** The concept is to use a specific keyword (or set of keywords) that, when processed, causes a temporary **up-weighting** of attention or activation in the layers responsible for reasoning. This can:
    * **Reinforce reasoning:** Encourage the model to spend more internal cycles on logical checking.
    * **Focus the reasoning:** Direct the model's internal thought process toward specific concepts or constraints critical to the problem.

This is a subtle, advanced technique that goes beyond surface-level prompt engineering, touching on the control mechanisms of the underlying LLM architecture.

---

## Key Takeaways

* **Model Selection is Crucial:** The choice between a **Base Model** (for new skills), a **Chat/Instruct Model** (for conversation), or a **Hybrid Model** (for SOTA performance) directly impacts project feasibility and outcome.
* **CoT is Low-Cost, High-Reward:** Simple phrases like `"Please think step by step."` are a powerful, almost zero-cost method for boosting the reasoning capabilities of most modern LLMs.
* **Control the Process, Not Just the Output:** Advanced LLM engineering is moving toward managing the model's internal state via techniques like **Budget Forcing** and **Weighted Keyword Reinforcement** to optimize for both performance and efficiency.


<!-- Adding a gray border in bottom of page. -->
```
```