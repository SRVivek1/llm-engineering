---
title: LLM Engineering Local Environment Setup Guide
permalink: AI-ML/llm/_topics/a1-local-setup.md
layout: course-content
date: October 30, 2025
---

Let's dive into setting up a robust local development environment suitable for begineer/intermediate LLM engineering tasks. We focus on modern, efficient tools like **Ollama** for running models locally and **uv** as an ultrafast python package manager.

## Table of Contents

- [Table of Contents](#table-of-contents)
- [1. Overview](#1-overview)
- [2. Ollama Installation for Local Models](#2-ollama-installation-for-local-models)
  - [Installation Instructions](#installation-instructions)
  - [Post-Installation Verification](#post-installation-verification)
  - [API verification](#api-verification)
- [3. Integrated Development Environment (IDE) Setup](#3-integrated-development-environment-ide-setup)
  - [IDE Choice and Update](#ide-choice-and-update)
  - [Required Extensions (VS Code/Cursor)](#required-extensions-vs-codecursor)
- [4. The `uv` Python Package and Project Manager](#4-the-uv-python-package-and-project-manager)
  - [Installation of `uv`](#installation-of-uv)
  - [Verification and Maintenance](#verification-and-maintenance)
- [5. Building the Python Project](#5-building-the-python-project)
  - [Project Synchronization](#project-synchronization)
- [6. Troubleshooting: Missing Jupyter Kernel](#6-troubleshooting-missing-jupyter-kernel)
  - [Manual Kernel Registration Steps](#manual-kernel-registration-steps)
- [7. Conclusion and Key Takeaways](#7-conclusion-and-key-takeaways)
  - [Key Takeaways](#key-takeaways)

-----

## 1\. Overview

A stable, performant local environment is critical for iterating quickly on LLM projects. This setup utilizes **Ollama** for running open-source models (like Llama 3 or Mistral) directly on your machine and **VS Code/Cursor** as the primary development platform, enhanced by the Rust-based package manager **uv** for superior speed and reliability.

---

## 2\. Ollama Installation for Local Models

**Ollama** simplifies running and managing large language models locally. It provides a single executable for downloading, configuring, and serving models via an API.

### Installation Instructions

Follow the platform-specific instructions below. The primary goal is to install the `ollama` command-line tool.

  * **Linux (Recommended via Script):**
    The installation script automatically handles setting up the service.
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
  * **macOS and Windows (GUI/Installer):**
    For these platforms, use the dedicated installers which often include a graphical user interface (GUI) and better system integration.
      * **macOS Installer:** [Download Ollama for Mac](https://ollama.com/download/mac)
      * **Windows Installer:** [Download Ollama for Windows](https://ollama.com/download/windows)

### Post-Installation Verification

Once installed, you can pull and run your first model, for example, the tiny `llama3:8b` model:

```bash
ollama run llama3:8b
```

This command downloads the model if it's not present and starts an interactive chat session via ***terminal/CMD***.


### API verification
You can run below curl command from terminal or use any availale HTTP Client tool to mimic below request and send the message to Ollama API. 
  * If the provided LLM model is available locally, `Ollama` with run the model and servs the request. While running model in this way Ollama sets a default max-life of 4 Minutes for that model post which the model will be terminated automatically.
  * `Stream` property is be default set to `True`. This enables the Ollama to keep sending the data to terminal as the model thinks and generates the response but if set to `False` it will process the request and send only the final response back to requestor.

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma3:1b",
    "messages": [{"role": "user", "content": "Tell me a fun fact"}],
    "stream": false
  }'
```
---

## 3\. Integrated Development Environment (IDE) Setup

For LLM engineering, an IDE with robust support for **Python**, **Jupyter Notebooks**, and **AI-assisted coding assistand** is essential.

### IDE Choice and Update

  * **Recommended IDEs:** **Visual Studio Code (VS Code)** or **Cursor**. 
    * Cursor is often preferred for its built-in, deep AI coding agent capabilities, but VS Code is the industry standard.
  * **Action:** Ensure you are running the **latest stable version** of your chosen IDE for the best feature and security support.

### Required Extensions (VS Code/Cursor)

Two core extensions from Microsoft are necessary to support a modern Python and data science workflow:

1.  **Python Extension (Microsoft):** Provides rich support for Python development, including IntelliSense, debugging, code navigation, and environment management.
      * *Tip:* Search the VS Code Marketplace for `ms-python.python`.
2.  **Jupyter Extension (Microsoft):** Enables full functionality for working with `.ipynb` files, including variable inspection, cell execution, and kernel management, crucial for research and prototyping in LLM development.
      * *Tip:* Search the VS Code Marketplace for `ms-toolsai.jupyter`.

---

## 4\. The `uv` Python Package and Project Manager

**uv** is an extremely fast and reliable Python package and project manager written in Rust, designed to be a drop-in replacement for common `pip`, `pip-tools`, and `virtualenv` workflows. It significantly accelerates dependency resolution and virtual environment creation.

### Installation of `uv`

The recommended method is via the installation script:

```bash
# Install uv via the official script
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verification and Maintenance

After installation, verify the version and know how to keep it updated:

  * **Verify Installation:**
    ```bash
    uv --version
    ```
  * **Update `uv`:**
    Keep your `uv` installation current to benefit from the latest speed improvements and features.
    ```bash
    uv self update
    ```

---

## 5\. Building the Python Project

Assuming you have a standard Python project structure and a `requirements.txt` or `pyproject.toml` file defining your dependencies, `uv` simplifies the process of creating a virtual environment (`venv`) and installing dependencies.

### Project Synchronization

The `uv sync` command is the equivalent of `pip install -r requirements.txt` or `pip-sync`, but much faster. It creates the virtual environment and installs/updates all dependencies defined in your project files.

```bash
# Command to build the virtual environment and install dependencies
uv sync
```

  * **Note:** If a `.venv` directory does not exist, `uv` will automatically create it based on your project files and then synchronize the required packages inside it.

-----

## 6\. Troubleshooting: Missing Jupyter Kernel

A common issue in IDEs like VS Code is the inability to detect the dedicated kernel within a new virtual environment when opening a Jupyter Notebook. This prevents running code cells with the project's specific dependencies.

To resolve this, manually register the virtual environment as a usable Jupyter kernel.

### Manual Kernel Registration Steps

1.  **Activate the Virtual Environment:** Navigate to your project root and activate the environment to ensure `uv` and `python` are linked to the correct binaries.

    ```bash
    source .venv/bin/activate
    ```

2.  **Run the `ipykernel` Install Command:** Use `uv run` to execute the Python interpreter within the virtual environment, calling the `ipykernel` module to register the environment.

      * `--user`: Installs the kernel for the current user.
      * `--name`: The internal name for the kernel (e.g., `llm-eng`).
      * `--display-name`: The name visible in the IDE's kernel selector.

    <!-- end list -->

    ```bash
    uv run python -m ipykernel install --user --name=llm-eng --display-name="LLM Eng (.venv)"
    ```

After running this, the kernel named **"LLM Eng (.venv)"** will appear in the kernel selector of your Jupyter Notebook in VS-Code, allowing you to execute the code blocks in `.ipynb` files directly from IDE with your project's installed packages.

---

## 7\. Conclusion and Key Takeaways

The modern LLM engineering workflow prioritizes speed and local experimentation. By leveraging **Ollama** for model serving and **uv** for dependency management, developers can achieve rapid iteration cycles.

### Key Takeaways

  * **Ollama:** Enables simple, powerful execution of open-source LLMs locally, reducing cloud costs during development.
  * **uv:** Drastically cuts down the time spent on dependency resolution and environment setup, freeing up time for actual engineering.
  * **IDE Setup:** Installing the **Python** and **Jupyter** extensions is non-negotiable for a professional LLM development experience.
  * **Kernel Registration:** Knowing how to manually register a kernel is an essential troubleshooting skill for any developer working with isolated Python environments and Jupyter notebooks.

Would you like to move on to documenting the LLM-specific techniques, such as **Prompt Engineering** and **RAG vs. Fine-Tuning**, that were mentioned in the session overview?


<!-- Adding a gray border in bottom of page. -->
```
```