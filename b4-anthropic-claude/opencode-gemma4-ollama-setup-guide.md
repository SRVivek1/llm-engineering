# OpenCode + Gemma 4 + Ollama: Local AI Agent Setup Guide

> Run a fully local, cost-free AI coding agent using Google's Gemma 4 MoE model, Ollama, and OpenCode — no cloud API keys required.

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 [Ollama](#11-ollama)
   - 1.2 [Gemma 4](#12-gemma-4)
   - 1.3 [OpenCode](#13-opencode)
2. [Feasibility Analysis](#2-feasibility-analysis)
3. [System Requirements](#3-system-requirements)
   - 3.1 [Hardware Requirements by Model Variant](#31-hardware-requirements-by-model-variant)
   - 3.2 [CPU-Only Machines](#32-cpu-only-machines)
   - 3.3 [Performance Expectations](#33-performance-expectations)
4. [Architecture Overview](#4-architecture-overview)
5. [Pre-Installation Checklist](#5-pre-installation-checklist)
6. [System Setup](#6-system-setup)
   - 6.1 [Install Ollama](#61-install-ollama)
   - 6.2 [Pull Gemma 4 Model](#62-pull-gemma-4-model)
   - 6.3 [Configure Ollama for Coding Workloads](#63-configure-ollama-for-coding-workloads)
   - 6.4 [Install OpenCode](#64-install-opencode)
   - 6.5 [Configure OpenCode to Use Local Ollama](#65-configure-opencode-to-use-local-ollama)
   - 6.6 [Verify the Setup End-to-End](#66-verify-the-setup-end-to-end)
7. [Model Selection Guide](#7-model-selection-guide)
8. [Advanced Configuration](#8-advanced-configuration)
   - 8.1 [Ollama Modelfile Tuning](#81-ollama-modelfile-tuning)
   - 8.2 [OpenCode Agent Customization](#82-opencode-agent-customization)
   - 8.3 [GPU Optimisation](#83-gpu-optimisation)
9. [Troubleshooting](#9-troubleshooting)
10. [Tips & Best Practices](#10-tips--best-practices)
11. [References](#11-references)

---

## 1. Introduction

### 1.1 Ollama

Ollama is an open-source runtime that makes running large language models (LLMs) on your local machine as simple as `ollama run <model>`. It packages model weights, a lightweight inference server, and a straightforward CLI into a single binary. Ollama exposes an OpenAI-compatible REST API on `http://localhost:11434/v1`, which means any tool that can talk to the OpenAI API can transparently point at your local model instead. It manages model downloads, quantization, GPU/CPU offloading, and memory management automatically. Ollama supports NVIDIA GPUs (via CUDA), AMD GPUs (via ROCm), Apple Silicon and Intel Macs (via Metal), and pure CPU inference — making it portable across virtually every developer machine. It is available on macOS, Linux, and Windows and has a thriving registry of hundreds of pre-built model variants.

- Official site: https://ollama.com
- Documentation: https://docs.ollama.com
- GitHub: https://github.com/ollama/ollama

### 1.2 Gemma 4

Gemma 4 is Google's fourth-generation family of open-weight language models released in 2025. It introduces a Mixture-of-Experts (MoE) architecture at the 26B parameter scale, alongside smaller dense edge variants (E2B and E4B) designed for on-device and laptop inference. The MoE design means the 26B model activates only ~4 billion parameters per forward pass (routing through 8 of 128 experts), delivering quality comparable to a full 31B dense model at a fraction of the compute cost. Gemma 4 supports a 256K token context window (26B/31B variants) or 128K (edge variants), multi-modal inputs (text + image for larger variants, plus audio for edge variants), and ships in both 16-bit (BF16) and quantized (8-bit, 4-bit, 2-bit) formats. For local inference the Q4_K_M quantization sweet-spot gives roughly 80–90% of BF16 quality at 25–30% of the VRAM cost.

- Model card: https://ai.google.dev/gemma/docs/core/model_card_4
- HuggingFace: https://huggingface.co/google/gemma-4
- Ollama registry: https://ollama.com/library/gemma4

### 1.3 OpenCode

OpenCode is an open-source, terminal-native AI coding agent built for developers who live in the command line. It integrates with 75+ LLM providers — including local models via Ollama — and offers agentic workflows: it can read files, run shell commands, make edits, search the web, and use MCP (Model Context Protocol) servers autonomously within your project. OpenCode is privacy-first with no telemetry, supports Language Server Protocol (LSP) for code intelligence, and is configurable via a simple JSON file. Unlike GUI-heavy alternatives it has minimal overhead and integrates naturally with existing terminal workflows, tmux setups, and CI pipelines. It is installed as a single binary or via npm and is available on macOS, Linux, and Windows.

- Official site: https://opencode.ai
- Documentation: https://opencode.ai/docs
- GitHub: https://github.com/opencode-ai/opencode

---

## 2. Feasibility Analysis

Running a fully local AI coding agent is feasible today for most developer machines but comes with important trade-offs depending on hardware.

| Scenario | Recommended Model | Feasibility | Notes |
|---|---|---|---|
| MacBook Pro M2/M3 (16GB unified RAM) | `gemma4:e4b` or `gemma4:26b` Q4 | ✅ Feasible | Apple Metal offloads all layers; 26B at Q4 fits in 16GB |
| MacBook Pro M3 Max (48GB+) | `gemma4:26b` Q8 or BF16 | ✅ Excellent | Enough VRAM for near-full quality |
| Linux/Windows + NVIDIA RTX 3090/4090 (24GB VRAM) | `gemma4:26b` Q4_K_M | ✅ Feasible | ~15.6GB VRAM required; slight overflow to RAM is OK |
| Linux/Windows + NVIDIA RTX 3070 (8GB VRAM) | `gemma4:e4b` Q4 | ⚠️ Partial GPU | E4B fits GPU; 26B will heavily spill to CPU RAM |
| CPU-only laptop (16GB RAM) | `gemma4:e2b` Q4 | ⚠️ Slow | ~3.2GB RAM; usable but 2-8 tokens/sec |
| CPU-only laptop (32GB RAM) | `gemma4:e4b` Q4 | ⚠️ Moderate | Better quality; still slow for large contexts |
| CPU-only laptop (<16GB RAM) | Not recommended | ❌ Not practical | System will swap heavily; essentially unusable |

### Key Feasibility Challenges

**1. MoE Memory Loading**
Despite activating only ~4B parameters per token, the 26B MoE model must load *all 26 billion weights* into memory for the expert routing table to function. This makes the VRAM/RAM requirement indistinguishable from a 26B dense model at the same quantization level. You do not save memory — you save compute per token.

**2. Quantization vs. Quality**
At Q4_K_M the 26B model is very capable for code generation. At Q2 quantization quality degrades noticeably. If your machine can only fit Q2, the E4B at Q4 will likely produce better results.

**3. Context Window vs. VRAM**
Gemma 4 supports up to 256K context tokens, but KV-cache for long contexts consumes substantial additional VRAM (roughly 1–4GB extra per 32K tokens at 26B scale). Ollama auto-scales context based on available VRAM — on constrained machines it will cap at 4K by default unless you explicitly configure it.

**4. Inference Speed on CPU**
CPU inference with llama.cpp (Ollama's backend) runs at roughly 2–8 tokens/second for 26B models on a modern laptop CPU. This is usable for interactive chat but creates frustrating delays in agentic loops where the model calls many tools in sequence.

**5. Concurrent Use**
Running other applications (browser, IDE, Docker containers) alongside Ollama competes for the same RAM/VRAM. Close memory-heavy apps before starting inference sessions.

---

## 3. System Requirements

### 3.1 Hardware Requirements by Model Variant

#### Storage (Disk) Requirements

| Model Tag | Quantization | Disk Size |
|---|---|---|
| `gemma4:e2b` | Q4_K_M (default) | ~1.5 GB |
| `gemma4:e4b` | Q4_K_M (default) | ~3 GB |
| `gemma4:26b` | Q4_K_M (default) | ~15.6 GB |
| `gemma4:26b` | Q8 | ~25 GB |
| `gemma4:26b` | BF16 | ~48 GB |
| `gemma4:31b` | Q4_K_M | ~17.4 GB |

#### RAM / VRAM Requirements

| Model | Q4_K_M | Q8 | BF16 |
|---|---|---|---|
| E2B | 3.2 GB | 4.6 GB | 9.6 GB |
| E4B | 5 GB | 7.5 GB | 15 GB |
| 26B MoE | **15.6 GB** | 25 GB | 48 GB |
| 31B dense | 17.4 GB | 30.4 GB | 58.3 GB |

> **Note:** Add ~1–4 GB per 32K extra context tokens to the above figures for KV-cache.

#### Minimum Recommended Hardware per Use Case

| Use Case | CPU | RAM | GPU VRAM | Storage |
|---|---|---|---|---|
| Edge / lightweight (`e4b`) | 4-core modern | 16 GB | 6 GB (optional) | 10 GB free |
| Main coding agent (`26b`) | 8-core modern | 32 GB | 16 GB | 30 GB free |
| High-quality full context | 12-core modern | 64 GB | 24 GB+ | 60 GB free |

### 3.2 CPU-Only Machines

Running Gemma 4 purely on CPU is possible via Ollama's llama.cpp backend but has significant limitations:

**What works:**
- All Gemma 4 variants run on CPU with no GPU required
- Ollama automatically detects no GPU and falls back to CPU
- No additional configuration is needed

**What to expect:**
- Inference speed: 2–8 tokens/sec for `gemma4:26b` on a modern 8-core CPU
- Inference speed: 10–25 tokens/sec for `gemma4:e4b` on the same CPU
- Agentic tasks that require many model calls will feel slow

**Optimisation flags for CPU:**

```bash
# Set thread count to your physical core count (not hyperthreaded)
OLLAMA_NUM_THREADS=8 ollama serve

# Or via Modelfile
PARAMETER num_thread 8
```

**Recommendation for CPU-only machines:**
- Use `gemma4:e4b` at Q4_K_M — it gives the best quality-per-second on CPU
- Keep context short (4K–8K tokens) to reduce processing time
- Disable other browser tabs and background processes

### 3.3 Performance Expectations

| Hardware | Model | Tokens/sec | Agentic Task Time |
|---|---|---|---|
| Apple M3 Max (48GB) | 26B Q8 | 35–50 | Fast (seconds per step) |
| Apple M2 Pro (16GB) | 26B Q4 | 15–25 | Moderate (5–15s per step) |
| RTX 4090 (24GB) | 26B Q4 | 40–60 | Fast |
| RTX 3070 (8GB) | E4B Q4 | 25–40 | Moderate |
| CPU only (16 cores) | E4B Q4 | 10–20 | Slow (20–60s per step) |
| CPU only (8 cores) | E4B Q4 | 5–12 | Very slow |

> **Rule of thumb:** For a usable agentic coding experience, target ≥15 tokens/sec sustained throughput.

---

## 4. Architecture Overview

Understanding how these three components interact helps debug issues and tune performance.

```
┌──────────────────────────────────────────────────────┐
│                   Developer Terminal                  │
│                                                       │
│   opencode (AI coding agent)                         │
│   ├── reads/writes project files                     │
│   ├── runs shell commands                            │
│   ├── calls LSP language servers                     │
│   └── sends inference requests ──────────────────┐  │
│                                                    │  │
└────────────────────────────────────────────────────┼──┘
                                                     │
                     HTTP (OpenAI-compatible API)    │
                     http://localhost:11434/v1        │
                                                     ▼
┌──────────────────────────────────────────────────────┐
│                  Ollama Server (:11434)               │
│   ├── model registry & download management          │
│   ├── quantization layer                            │
│   ├── context/KV-cache management                   │
│   └── inference backend (llama.cpp) ─────────────┐ │
│                                                    │ │
└────────────────────────────────────────────────────┼─┘
                                                     │
                     weights loaded into memory       │
                                                     ▼
┌──────────────────────────────────────────────────────┐
│              Gemma 4 Model (gemma4:26b)               │
│   ├── MoE router (selects 8 of 128 experts)         │
│   ├── transformer layers (weights in RAM/VRAM)      │
│   └── KV-cache (grows with context length)          │
└──────────────────────────────────────────────────────┘
```

**Data flow for a single coding step:**
1. You type a prompt in OpenCode's terminal UI
2. OpenCode collects project context (files, LSP diagnostics, tool results) and assembles a prompt
3. OpenCode sends a `/chat/completions` request to `http://localhost:11434/v1`
4. Ollama forwards the tokenized request to llama.cpp running Gemma 4
5. Gemma 4's MoE router activates the relevant experts, generates tokens
6. Tokens stream back to OpenCode, which renders them and executes any tool calls
7. Tool results feed back as new context into the next model call

---

## 5. Pre-Installation Checklist

Before running any install commands, verify:

- [ ] **Disk space:** At least 20 GB free (30 GB recommended for `gemma4:26b`)
- [ ] **RAM:** Check with `free -h` (Linux) or Activity Monitor (macOS)
- [ ] **GPU check (NVIDIA):** `nvidia-smi` — note VRAM column
- [ ] **GPU check (Apple Silicon):** Unified memory is shared; check total in About This Mac
- [ ] **macOS version:** Ollama requires macOS 12 Monterey or later
- [ ] **Linux kernel:** 5.4+ for ROCm; any modern kernel for CPU/NVIDIA
- [ ] **Internet connection:** Required for initial model download (~16 GB for `gemma4:26b`)
- [ ] **Node.js:** Version 18+ if installing OpenCode via npm (`node --version`)
- [ ] **Package manager:** Homebrew (macOS) or system package manager (Linux)

---

## 6. System Setup

### 6.1 Install Ollama

#### macOS

```bash
# Option A: Homebrew (recommended)
brew install ollama

# Option B: Download installer
# Visit https://ollama.com/download/mac and run the .dmg
```

#### Linux

```bash
# Official install script (handles NVIDIA/AMD GPU driver detection automatically)
curl -fsSL https://ollama.com/install.sh | sh

# The script installs a systemd service; verify it is running:
sudo systemctl status ollama
```

#### Windows

Download and run the installer from https://ollama.com/download/windows. Ollama installs as a background service and adds `ollama` to your PATH.

#### Verify Installation

```bash
ollama --version
# Expected output: ollama version 0.21.0 (or later)
```

#### Start the Ollama Service

On macOS and Windows, Ollama starts automatically. On Linux:

```bash
# Start manually (foreground, for testing)
ollama serve

# Or ensure the systemd service is enabled
sudo systemctl enable --now ollama
```

---

### 6.2 Pull Gemma 4 Model

With Ollama running, download your chosen Gemma 4 variant. The download only happens once; subsequent starts load from disk.

```bash
# Recommended for most developers (26B MoE, Q4 quantization, ~15.6GB)
ollama pull gemma4:26b

# Lightweight option for machines with <16GB RAM (4B edge, ~3GB)
ollama pull gemma4:e4b

# Smallest edge variant (2B, ~1.5GB) — very fast but less capable
ollama pull gemma4:e2b
```

Monitor download progress in the terminal. Downloads are resumable; if interrupted just run the same command again.

**Verify the model downloaded correctly:**

```bash
ollama list
# NAME           ID              SIZE    MODIFIED
# gemma4:26b     abc123def456    15.6GB  2 minutes ago

# Quick smoke test
ollama run gemma4:26b "Hello, respond in one sentence."
```

---

### 6.3 Configure Ollama for Coding Workloads

Ollama's defaults (2048 token context, conservative parallelism) are not optimised for agentic coding agents. Apply these settings before starting OpenCode.

#### Option A: Environment Variables (Recommended for Quick Start)

```bash
# Set context window to 32K tokens (suitable for most coding tasks)
export OLLAMA_CONTEXT_LENGTH=32768

# Set thread count to your physical core count
export OLLAMA_NUM_THREADS=8   # adjust to your CPU core count

# Optional: limit to one parallel request (reduces memory pressure on smaller machines)
export OLLAMA_NUM_PARALLEL=1

# Start Ollama with these settings
ollama serve
```

To make these persistent, add the `export` lines to your `~/.zshrc` or `~/.bashrc`.

On Linux with systemd, add environment variables to the service:

```bash
sudo systemctl edit ollama
```

Add these lines in the editor:

```ini
[Service]
Environment="OLLAMA_CONTEXT_LENGTH=32768"
Environment="OLLAMA_NUM_THREADS=8"
```

Then reload:

```bash
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

#### Option B: Custom Modelfile (Recommended for Fine-Tuned Control)

Create a Modelfile that permanently bakes your settings into a named model variant:

```bash
mkdir -p ~/.ollama/models
cat > ~/.ollama/models/Modelfile.gemma4-code << 'EOF'
FROM gemma4:26b

# Context window — 32K is a good balance of capability and VRAM use
PARAMETER num_ctx 32768

# Thread count — set to your CPU's physical core count
PARAMETER num_thread 8

# GPU layers — set to 999 to offload all layers (Ollama caps at available layers)
PARAMETER num_gpu 999

# Temperature — lower = more deterministic code generation
PARAMETER temperature 0.2

# System prompt optimised for coding
SYSTEM """
You are an expert software engineer. Produce clean, correct, idiomatic code.
When asked to edit files, always show the full modified file.
When explaining, be concise and precise.
"""
EOF

# Build the custom model
ollama create gemma4-code -f ~/.ollama/models/Modelfile.gemma4-code

# Verify it appears in the model list
ollama list
```

You will reference `gemma4-code` (not `gemma4:26b`) in OpenCode's config when using this approach.

---

### 6.4 Install OpenCode

#### macOS

```bash
# Option A: Official install script
curl -fsSL https://opencode.ai/install | bash

# Option B: Homebrew
brew install opencode

# Option C: npm (requires Node.js 18+)
npm install -g opencode-ai@latest
```

#### Linux

```bash
# Official install script
curl -fsSL https://opencode.ai/install | bash

# Arch Linux (AUR)
pacman -S opencode

# npm
npm install -g opencode-ai@latest
```

#### Windows

```powershell
# Scoop
scoop install opencode

# npm
npm install -g opencode-ai@latest
```

#### Verify Installation

```bash
opencode --version
```

---

### 6.5 Configure OpenCode to Use Local Ollama

OpenCode reads configuration from (in order of precedence):

1. `./.opencode.json` — project-level config (committed to git, shared with team)
2. `~/.config/opencode/opencode.json` — user-level global config
3. `~/.opencode.json` — user-level fallback

For a personal local setup, use the user-level config:

```bash
mkdir -p ~/.config/opencode
```

Create `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "gemma4:26b": {
          "name": "Gemma 4 26B MoE (local)"
        },
        "gemma4:e4b": {
          "name": "Gemma 4 4B Edge (local)"
        },
        "gemma4-code": {
          "name": "Gemma 4 26B Code (custom Modelfile)"
        }
      }
    }
  },
  "model": "ollama/gemma4:26b"
}
```

**Configuration fields explained:**

| Field | Purpose |
|---|---|
| `provider.ollama.npm` | Tells OpenCode which AI SDK adapter to use (`@ai-sdk/openai-compatible` for any OpenAI-compatible API) |
| `provider.ollama.options.baseURL` | Ollama's API endpoint |
| `provider.ollama.models` | Map of Ollama model IDs to human-readable display names shown in OpenCode's model picker |
| `model` | Default model to use when OpenCode starts (`<provider>/<model-id>` format) |

#### Quick Setup via Ollama Launch (Alternative)

Ollama 0.21+ includes a one-command integration:

```bash
ollama launch opencode
```

This automatically injects the Ollama provider configuration into OpenCode via the `OPENCODE_CONFIG_CONTENT` environment variable, merging with any existing local config. It is a quick way to get started without manually editing JSON.

---

### 6.6 Verify the Setup End-to-End

```bash
# 1. Confirm Ollama is running and the model is loaded
ollama ps
# NAME         ID     SIZE    PROCESSOR  UNTIL
# gemma4:26b   ...    15.6GB  100% GPU   forever

# 2. Test the Ollama API directly
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4:26b",
    "messages": [{"role": "user", "content": "Write a Python hello world in one line."}],
    "stream": false
  }' | python3 -m json.tool

# 3. Launch OpenCode
opencode

# Inside OpenCode, run:
# /model            → should show gemma4:26b as selected
# Write a simple hello world in Go.
```

A successful setup shows the model generating code in the OpenCode terminal UI without any "provider not found" or connection errors.

---

## 7. Model Selection Guide

Use this flowchart to pick the right Gemma 4 variant for your machine:

```
Do you have a GPU with ≥16GB VRAM (or Apple Silicon ≥16GB unified)?
  ├─ YES → gemma4:26b Q4_K_M  ← Best quality for local coding
  │         (15.6GB VRAM, ~35–60 tokens/sec on GPU)
  │
  └─ NO → Do you have ≥8GB RAM free (CPU or small GPU)?
            ├─ YES → gemma4:e4b Q4_K_M  ← Best quality/speed balance
            │         (~5GB RAM, ~10–25 tokens/sec CPU)
            │
            └─ NO → gemma4:e2b Q4_K_M  ← Minimum viable option
                      (~3.2GB RAM, ~15–30 tokens/sec CPU)
```

**Quick reference:**

| Priority | Choose |
|---|---|
| Best code quality | `gemma4:26b` or `gemma4:31b` |
| Best speed on small GPU | `gemma4:e4b` |
| Minimum footprint | `gemma4:e2b` |
| Long context (>32K tokens) | `gemma4:26b` with `OLLAMA_CONTEXT_LENGTH=65536` |

---

## 8. Advanced Configuration

### 8.1 Ollama Modelfile Tuning

Fine-tune inference behaviour by adjusting Modelfile `PARAMETER` values:

```dockerfile
FROM gemma4:26b

# --- Memory & Performance ---
PARAMETER num_ctx 16384        # Context window (tokens). Higher = more VRAM
PARAMETER num_gpu 999          # GPU layers to offload (999 = all)
PARAMETER num_thread 8         # CPU threads (set to physical core count)
PARAMETER num_batch 512        # Batch size. Higher = faster but more VRAM

# --- Output Quality ---
PARAMETER temperature 0.1      # 0.0 = deterministic, 1.0 = creative
PARAMETER top_p 0.9            # Nucleus sampling threshold
PARAMETER top_k 40             # Top-K sampling (lower = more focused)
PARAMETER repeat_penalty 1.1   # Penalise repeated tokens

# --- Flash Attention (Gemma 4 supports this in Ollama 0.21+) ---
PARAMETER flash_attn true      # Significantly reduces VRAM for long contexts
```

**Rebuild after any Modelfile change:**

```bash
ollama create gemma4-code -f ./Modelfile.gemma4-code
```

### 8.2 OpenCode Agent Customization

Create an `AGENTS.md` file in your project root. OpenCode reads this to understand project-specific conventions and commit it to git:

```bash
opencode init
```

This creates a template `AGENTS.md` that you can customise with your project's coding standards, preferred patterns, and agent behaviour instructions.

**Extended OpenCode config with agent settings:**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "gemma4:26b": {
          "name": "Gemma 4 26B MoE"
        }
      }
    }
  },
  "model": "ollama/gemma4:26b",
  "autoshare": false,
  "autoapprove": false
}
```

### 8.3 GPU Optimisation

#### NVIDIA (CUDA)

```bash
# Check available VRAM before loading model
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv

# Set GPU layers explicitly (useful when model partially fits GPU)
# For 26B Q4 with 16GB VRAM, offload ~30 of 46 layers
OLLAMA_NUM_GPU=30 ollama serve
```

#### AMD (ROCm)

```bash
# Ollama auto-detects ROCm; verify with:
ollama run gemma4:e4b "hello" --verbose 2>&1 | grep -i "gpu\|rocm"
```

#### Apple Silicon (Metal)

No extra configuration needed. Ollama uses Metal by default on Apple Silicon and shares unified memory between CPU and GPU, which means Gemma 4 26B at Q4 can fit entirely in GPU memory on M2 Pro (16GB) or higher.

```bash
# Verify Metal is being used
ollama run gemma4:26b "hello" --verbose 2>&1 | grep -i metal
```

---

## 9. Troubleshooting

### Ollama won't start / port 11434 already in use

```bash
# Check what is using the port
lsof -i :11434

# Kill the conflicting process (replace <PID>)
kill -9 <PID>

# Restart Ollama
ollama serve
```

### Model download fails or is interrupted

```bash
# Simply re-run the pull command — Ollama resumes from where it stopped
ollama pull gemma4:26b
```

### OpenCode cannot connect to Ollama

```bash
# 1. Confirm Ollama is running
curl http://localhost:11434/api/tags

# 2. Check the baseURL in your opencode.json matches exactly:
cat ~/.config/opencode/opencode.json | grep baseURL
# Should be: "http://localhost:11434/v1"

# 3. If running Ollama in Docker or a VM, replace localhost with the container IP
```

### "Model not found" error in OpenCode

```bash
# List models Ollama knows about
ollama list

# The model ID in opencode.json must match exactly (including the tag)
# If you pulled gemma4:26b, the key in "models" must be "gemma4:26b"
```

### Out of memory (OOM) / model gets killed

```bash
# 1. Check current memory usage
ollama ps   # shows model size in RAM/VRAM

# 2. Switch to a smaller quantization or model variant
ollama pull gemma4:e4b   # much smaller footprint

# 3. Reduce context window
export OLLAMA_CONTEXT_LENGTH=4096
ollama serve

# 4. Close competing applications (browsers, Docker containers)
```

### Slow inference (< 5 tokens/sec)

```bash
# 1. Check if GPU is being used
ollama run gemma4:26b "hi" --verbose 2>&1 | grep -E "gpu|layers"
# Look for "offloaded X/Y layers to GPU"

# 2. If 0 layers on GPU, check GPU drivers
nvidia-smi          # NVIDIA
rocm-smi            # AMD

# 3. Reduce context length to free VRAM for more GPU layers
export OLLAMA_CONTEXT_LENGTH=8192

# 4. On CPU-only: increase thread count
export OLLAMA_NUM_THREADS=$(nproc)   # Linux
export OLLAMA_NUM_THREADS=$(sysctl -n hw.physicalcpu)   # macOS
```

### OpenCode shows no models in the model picker

```bash
# Verify the provider config is syntactically valid JSON
cat ~/.config/opencode/opencode.json | python3 -m json.tool

# Check the npm field — it must be exactly "@ai-sdk/openai-compatible"
# Check the baseURL has no trailing slash after /v1
```

### Gemma 4 gives poor code quality

- Switch from Q2 to Q4_K_M quantization: `ollama pull gemma4:26b:q4_K_M`
- Increase context length — the model performs better with more project context
- Use a system prompt via Modelfile (see [Section 8.1](#81-ollama-modelfile-tuning))
- Lower temperature to 0.1–0.2 for more deterministic code output

### Flash attention errors (Ollama 0.21+)

```bash
# If flash_attn causes errors on older GPUs, disable it
PARAMETER flash_attn false
```

---

## 10. Tips & Best Practices

**Choosing the right quantization**
Start with `Q4_K_M` (the default for most `ollama pull` commands). It offers the best balance of quality and memory use. Only go to Q8 if you have VRAM headroom and want better quality on subtle reasoning tasks.

**Context length strategy**
Bigger context = better agent performance but more VRAM. A practical starting point is 16K–32K. Only bump to 64K+ if you are working with large codebases and find the model losing track of earlier context. Monitor VRAM with `nvidia-smi` or Activity Monitor before increasing.

**Keep Ollama running as a background service**
Rather than starting `ollama serve` in a terminal each time, let it run as a service. On macOS it starts automatically; on Linux enable the systemd service. This way OpenCode can start instantly without waiting for the server.

**Use a project-level AGENTS.md**
Commit an `AGENTS.md` to your repository with your coding conventions, forbidden patterns, and test instructions. OpenCode reads this and follows it for every session — a one-time investment that consistently improves output quality.

**Pre-warm the model**
The first request after loading a model is slow (model weights stream from disk to VRAM). Send a short warmup prompt after starting Ollama:

```bash
ollama run gemma4:26b "ready" > /dev/null
```

**Limit to one model at a time**
Ollama can load multiple models simultaneously, but each consumes full VRAM. Set `OLLAMA_MAX_LOADED_MODELS=1` to ensure only one model is resident, freeing all available VRAM for the active model.

```bash
export OLLAMA_MAX_LOADED_MODELS=1
```

**Monitor resource usage during sessions**
Keep a terminal with `watch -n 2 nvidia-smi` (NVIDIA) or `watch -n 2 ollama ps` open while working. This gives immediate feedback when the model is GPU-bound vs. CPU-bound and helps you tune settings.

**Network isolation for privacy**
Ollama binds to `127.0.0.1` by default — only accessible from localhost. If you are on a shared network and want to ensure no accidental external access, verify this with:

```bash
ss -tlnp | grep 11434    # Linux
lsof -i :11434           # macOS
```

**Update Ollama and models regularly**
Ollama releases frequently and often includes performance improvements for specific model architectures (e.g., flash attention support for Gemma 4 was added in 0.21). Keep it updated:

```bash
brew upgrade ollama        # macOS
curl -fsSL https://ollama.com/install.sh | sh   # Linux (re-runs updater)
```

**Pair with a fast edge model for quick queries**
Pull `gemma4:e4b` alongside `gemma4:26b`. For quick one-line questions or small edits, switching to the E4B model via `/model` in OpenCode gives 3–5x faster responses at minimal quality cost.

---

## 11. References

### Official Documentation

| Resource | URL |
|---|---|
| Ollama official site | https://ollama.com |
| Ollama CLI docs | https://docs.ollama.com/cli |
| Ollama context length guide | https://docs.ollama.com/context-length |
| Ollama GitHub | https://github.com/ollama/ollama |
| Ollama–OpenCode integration | https://docs.ollama.com/integrations/opencode |
| OpenCode official site | https://opencode.ai |
| OpenCode documentation | https://opencode.ai/docs |
| OpenCode providers config | https://opencode.ai/docs/providers |
| OpenCode GitHub | https://github.com/opencode-ai/opencode |
| Gemma 4 model card | https://ai.google.dev/gemma/docs/core/model_card_4 |
| Gemma 4 overview (Google AI) | https://ai.google.dev/gemma/docs/core |
| Gemma 4 on HuggingFace | https://huggingface.co/google/gemma-4 |
| Gemma 4 on Ollama registry | https://ollama.com/library/gemma4 |

### Further Reading

| Topic | Resource |
|---|---|
| Understanding MoE architecture | https://huggingface.co/blog/moe |
| llama.cpp (Ollama's inference backend) | https://github.com/ggml-org/llama.cpp |
| GGUF quantization formats explained | https://huggingface.co/docs/hub/en/gguf |
| Model Context Protocol (MCP) for OpenCode | https://modelcontextprotocol.io |
| ROCm GPU support on Linux | https://rocm.docs.amd.com |
| CUDA installation guide | https://docs.nvidia.com/cuda/cuda-installation-guide-linux |

---

*Last updated: April 2026 | Ollama v0.21.0 | Gemma 4 | OpenCode latest*
