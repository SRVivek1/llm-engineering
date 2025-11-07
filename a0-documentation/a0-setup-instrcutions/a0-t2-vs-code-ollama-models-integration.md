---
title: "Local AI Coding Setup: Continue Extension with Ollama in VS Code"
permalink: ai-ml/llm/_topics/a1-t8-vs-code-ollama-models-integration.md
layout: course-content
date: 2025-10-31
categories: llm-engineering
tags: [prompt-engineering, markdown]
---

# Local AI Coding Setup: Continue Extension with Ollama in VS Code

[![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)](https://code.visualstudio.com/) [![Ollama](https://img.shields.io/badge/Ollama-FF6B35?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/) [![Continue](https://img.shields.io/badge/Continue-0E1116?style=for-the-badge&logo=continue&logoColor=white)](https://continue.dev/)

Welcome to this fully **local, private, and offline** AI coding copilot setup! 🚀 Using the [Continue extension](https://continue.dev/) in VS Code paired with [Ollama](https://ollama.com/) for lightweight LLMs, you'll get autocomplete, chat, editing, and more—without cloud dependencies. Perfect for developers prioritizing speed, privacy, and customization.

This guide is battle-tested for macOS, Linux, and Windows. Expect setup in ~15-30 minutes, depending on model downloads.

## Table of Contents
- [Local AI Coding Setup: Continue Extension with Ollama in VS Code](#local-ai-coding-setup-continue-extension-with-ollama-in-vs-code)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Step 1: Install Continue Extension](#step-1-install-continue-extension)
  - [Step 2: Install and Start Ollama](#step-2-install-and-start-ollama)
    - [Installation Commands](#installation-commands)
    - [Verify and Start](#verify-and-start)
  - [Step 3: Download Local Models](#step-3-download-local-models)
    - [Key Commands](#key-commands)
  - [Step 4: Configure Continue with Ollama](#step-4-configure-continue-with-ollama)
    - [Base Config Example](#base-config-example)
    - [Apply Changes](#apply-changes)
  - [Step 5: Select and Use Your Models](#step-5-select-and-use-your-models)
  - [Model Recommendations](#model-recommendations)
  - [Tips for Performance](#tips-for-performance)
  - [Troubleshooting](#troubleshooting)
  - [Next Steps](#next-steps)

---

## Prerequisites
Before diving in, ensure your setup meets these basics. Use this checklist for a smooth ride! ✅

| Requirement          | Details                          | Why It Matters                  |
|----------------------|----------------------------------|---------------------------------|
| **VS Code** | Install Latest version   | Core IDE for the extension  |
| **RAM**  | 8GB minimum (16GB+ recommended) | Handles model inference |
| **Storage** | 10GB+ free   | For model files (e.g., 4-8GB each) |
| **OS**  | macOS, Linux, or Windows | Ollama compatibility  |
| **Terminal Access** | Basic command-line skills | For Ollama setup |

> 💡 **Pro Tip**: If you're on a laptop, plug in for downloads—models can be hefty!

---

## Step 1: Install Continue Extension
Get the AI brains into VS Code.

1. Open VS Code.
2. Hit `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS) to open Extensions.
3. Search for **"Continue"**.
4. Install the official extension from [Continue.dev](https://continue.dev/).  
<!-- ![Continue Icon](https://cdn.prod.website-files.com/663e06c56841363663ffbbcf/663e1b9fb023f0b622ad3608_log-text.svg) -->

5. Reload VS Code after install. 
   * You'll see a new **Continue** icon in the activity bar (left sidebar).

---

## Step 2: Install and Start Ollama
Ollama is your local LLM server—think of it as a lightweight OpenAI API alternative.

### Installation Commands
Run these in your terminal:

| OS       | Command  |
|-------- | ------------|
| **macOS** | `brew install ollama`  |
| **Linux** | `curl -fsSL https://ollama.com/install.sh \| sh`  |
| **Windows** | Download installer from [ollama.com](https://ollama.com/download) |

### Verify and Start
```bash
# Check version
ollama --version

# Start the server (runs in background)
ollama serve

# Test connection (should echo "Ollama is running")
curl http://localhost:11434
```

> ⚠️ **Warning**: Keep the terminal open or run `ollama serve` as a service (e.g., via systemd on Linux) for persistent use.

---

## Step 3: Download Local Models
Pull models from Ollama's library. Start small for testing!

### Key Commands
```bash
# General coding (balanced)
ollama pull llama3.2:3b

# Code-focused autocomplete
ollama pull qwen2.5-coder:1.5b-base

# Embeddings for search (RAG)
ollama pull nomic-embed-text:latest

# List all installed models
ollama list
```

> 🔍 **Quick Note**: Use `ollama run <model>` for interactive testing, but `pull` for setup. Tags like `:3b` specify size—stick to 1.5B-8B for everyday hardware.

---

## Step 4: Configure Continue with Ollama
Continue uses `~/.continue/config.yaml` (YAML for readability). 
* Open it via `Continue sidebar` > `Settings gear` > "`Open config.yaml`".

### Base Config Example
Here's a starter config with role-separated models for efficiency:

```yaml
#config
name: Local Config
version: 1.0.0
schema: v1
models:
  # Chats, edits, and apply changes (default for interactions)
  - name: Llama 3.2 3B
    provider: ollama
    model: llama3.2:3b
    roles:
      - chat
      - edit
      - apply
    default: true
    completionOptions:
      temperature: 0.2  # Low for consistent code
      maxTokens: 2048   # Balanced length

  # Lightweight autocomplete
  - name: Qwen2.5-Coder 1.5B
    provider: ollama
    model: qwen2.5-coder:1.5b-base
    # Note: Comment out below autocomplete role if facing performance issues. 
    # If enabled it will keep running the configured model.
    # Resulting in consuming a lot of CPU and RAM, specially if you have limited resources.
    roles:
      - autocomplete
    completionOptions:
      temperature: 0.1  # Focused predictions
      topP: 0.9

  # Embeddings for @codebase searches
  - name: Nomic Embed
    provider: ollama
    model: nomic-embed-text:latest
    roles:
      - embed

  # Auto-detect new models
  - name: Autodetect
    provider: ollama
    model: AUTODETECT

# Global tweaks
contextProviders:
  - name: code
    params:
      nRetrieve: 5  # Fast searches
      useReranking: false

tabAutocompleteOptions:
  enabled: true
  model: "Qwen2.5-Coder 1.5B"
```

### Apply Changes
- Save the file.
- Reload: `Cmd/Ctrl+Shift+P` > "Continue: Reload Config".
- Auto-detects Ollama at `http://localhost:11434`.

> 🎨 **UX Enhancement**: Use VS Code's YAML extension for syntax highlighting and validation—install via Extensions marketplace.

---

## Step 5: Select and Use Your Models
Time to code with AI! Open the Continue sidebar.

1. **Select Model**: Dropdown at top—pick "Llama 3.2 3B" (or your default).
2. **Core Features**:
   - **Chat**: Highlight code > `Cmd/Ctrl+L` > Ask "Refactor this?"
   - **Autocomplete**: Type code—suggestions pop up (Tab to accept).
   - **Edit**: Select code > `Cmd/Ctrl+I` > "Add error handling".
   - **Search**: In chat, type `@codebase What does utils.py do?`
3. **Agent Mode**: For tools, add `"capabilities": ["tool_use"]` to a model's config.

> 💫 **Pro Tip**: Pin your favorite model to the dropdown for one-click access.

---

## Model Recommendations
Tailor to your workflow. Smaller = faster on CPU.

| Use Case             | Model Suggestion              | RAM Estimate | Speed Rating |
|----------------------|-------------------------------|--------------|--------------|
| **Code Completion** | qwen2.5-coder:1.5b-base      | 4GB         | ⚡ Fast     |
| **General Coding**  | llama3.2:3b                  | 8GB         | 🚀 Quick    |
| **Advanced Tasks**  | codellama:7b                 | 8-16GB      | 🐌 Balanced |
| **Heavy Reasoning** | mistral:7b                   | 16GB+       | 🐢 Thoughtful |

Run `ollama pull <model>` to add more. For GPU boost (NVIDIA/AMD), Ollama auto-detects—monitor with `nvidia-smi`.

---

## Tips for Performance
- **Monitor Loads**: `ollama ps` in terminal.
- **Tune Context**: Lower `maxTokens` for speed.
- **GPU Tweaks**: In a custom Modelfile: `PARAMETER num_gpu 35`.
- **Remote Ollama**: Set `"apiBase": "http://your-server:11434"` in config.
- **Backup Config**: Git-track `~/.continue/` for version control.

> 🌟 **Enhancement**: Integrate with VS Code themes—Continue respects your dark/light mode for a seamless look.

---

## Troubleshooting
Hit a snag? Quick fixes:

| Issue                  | Solution                                                                 |
|------------------------|--------------------------------------------------------------------------|
| **Model 404 Error**   | `ollama pull <exact-tag>`; match config precisely.                      |
| **Connection Failed** | Restart `ollama serve`; check port 11434 (`netstat -an \| grep 11434`). |
| **Slow Autocomplete** | Switch to 1.5B model; reduce `contextLength`.                           |
| **No Embeddings**     | Pull `nomic-embed-text`; test with `@files` in chat.                    |
| **Logs Needed**       | Continue sidebar > Debug view.                                           |

For deep dives, check [Continue Docs](https://docs.continue.dev/) or [Ollama Guide](https://ollama.com/docs).

---

## Next Steps
- **Experiment**: Try `@terminal` for shell integration.
- **Scale Up**: Add larger models like `deepseek-coder:6.7b` once comfy.
- **Contribute**: Fork this guide on GitHub and PR enhancements!

Questions? Drop a comment or ping on [Continue Discord](https://discord.gg/continue). Happy local coding! 🛠️✨



```
```