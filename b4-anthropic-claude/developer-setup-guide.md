# Claude Code — Developer Setup Guide

A complete guide to installing Claude Code, authenticating, and performing an initial analysis of your project. Covers Windows, Linux, and macOS.

Official docs: https://docs.anthropic.com/en/claude-code

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Installation](#2-installation)
3. [Authentication](#3-authentication)
4. [Initial Project Analysis](#4-initial-project-analysis)
5. [Essential Commands Reference](#5-essential-commands-reference)
6. [Troubleshooting by OS](#6-troubleshooting-by-os)
7. [Common Gotchas](#7-common-gotchas)

---

## 1. System Requirements

| Platform | Minimum Version |
|---|---|
| macOS | 13.0 (Ventura) or later |
| Windows | 10 build 1809 / Server 2019 or later |
| Ubuntu | 20.04+ |
| Debian | 10+ |
| Alpine Linux | 3.19+ |

**Hardware:** 4 GB RAM minimum, x64 or ARM64 processor.

**Network:** Internet access required. Claude Code must be used from an [Anthropic-supported country](https://www.anthropic.com/supported-countries).

**Windows-only prerequisite:** [Git for Windows](https://git-scm.com/downloads/win) must be installed before Claude Code. It provides the Git Bash shell that Claude Code relies on.

---

## 2. Installation

### macOS

**Option A — curl installer (recommended, auto-updates):**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Installs to `~/.local/bin/claude` and automatically adds it to your PATH.

**Option B — Homebrew (manual updates):**

```bash
brew install --cask claude-code
```

Note: Homebrew does **not** auto-update. Run `brew upgrade claude-code` manually when needed.

**Verify installation:**

```bash
claude --version
claude doctor
```

---

### Linux (Ubuntu / Debian / Alpine)

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

If `~/.local/bin` is not in your PATH, add it:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# Reload
source ~/.bashrc
```

**Alpine Linux only** — install these dependencies first:

```bash
apk add libgcc libstdc++ ripgrep
```

Then set the following environment variable before installing:

```bash
export USE_BUILTIN_RIPGREP=0
curl -fsSL https://claude.ai/install.sh | bash
```

---

### Windows

**Option A — PowerShell (recommended, auto-updates):**

Open PowerShell as a regular user (not Administrator) and run:

```powershell
irm https://claude.ai/install.ps1 | iex
```

**Option B — Command Prompt:**

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

**Option C — WinGet (manual updates):**

```powershell
winget install Anthropic.ClaudeCode
```

**Option D — WSL 2 (Windows Subsystem for Linux):**

Open a WSL terminal (not PowerShell) and run the Linux installer:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

WSL 2 supports sandboxing; WSL 1 does not. If you use WSL 2 with sandboxing, install:

```bash
sudo apt-get install bubblewrap socat
```

**Verify installation (PowerShell or Git Bash):**

```powershell
claude --version
claude doctor
```

---

### npm Install (All Platforms, Legacy)

If you prefer npm and already have Node.js 18+ installed:

```bash
npm install -g @anthropic-ai/claude-code
```

This method does not auto-update. Prefer the native installer above.

---

## 3. Authentication

You have two main options. The `/login` OAuth flow is simplest for individual developers. An API key is preferred for automation, CI, or teams using the API tier.

### Option A — Login with Your Anthropic Account (Recommended)

This works with Claude Pro, Max, Team, and Enterprise subscriptions.

```bash
claude
```

On first launch Claude Code opens a browser login page automatically. Sign in with your Anthropic account.

If the browser does not open automatically:
- Press `c` in the terminal to copy the login URL, then paste it into your browser.
- If the browser shows a code instead of redirecting, paste that code back into the terminal.

You can also run `/login` inside an active session to re-authenticate:

```
/login
```

Credentials are stored securely:
- **macOS:** Keychain
- **Linux / Windows:** `~/.claude/.credentials.json` (permissions: `0600`)

**Check authentication status:**

```bash
claude auth status
```

---

### Option B — API Key

Get an API key from the [Anthropic Console](https://console.anthropic.com/). Then set the environment variable before starting Claude Code.

**macOS / Linux:**

```bash
export ANTHROPIC_API_KEY=sk-ant-...
claude
```

To make this permanent, add the export line to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.).

**Windows PowerShell (current session):**

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
claude
```

**Windows PowerShell (permanent, user-level):**

```powershell
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")
```

**Windows CMD:**

```batch
set ANTHROPIC_API_KEY=sk-ant-...
claude
```

**Important:** When `ANTHROPIC_API_KEY` is set, it takes priority over your subscription login. If you see a `403 Forbidden` error while having an active subscription, unset the variable:

```bash
unset ANTHROPIC_API_KEY   # macOS / Linux
```

```powershell
Remove-Item Env:ANTHROPIC_API_KEY   # Windows PowerShell
```

---

### Option C — Long-lived Token (for CI / Scripts)

For automation where you cannot use a browser:

```bash
claude setup-token
```

This generates a `CLAUDE_CODE_OAUTH_TOKEN` (valid for one year) that you can set as an environment variable in CI pipelines.

---

### Authentication Precedence

If multiple credentials are configured, Claude Code uses the first one it finds in this order:

1. Cloud provider env vars (Bedrock, Vertex AI, Foundry)
2. `ANTHROPIC_AUTH_TOKEN`
3. `ANTHROPIC_API_KEY`
4. `CLAUDE_CODE_OAUTH_TOKEN`
5. OAuth subscription login (the `/login` flow)

---

## 4. Initial Project Analysis

Once authenticated, navigate to your project directory and start Claude Code:

```bash
cd /path/to/your/project
claude
```

### Step 1 — Generate CLAUDE.md with `/init`

`CLAUDE.md` is a project-specific instruction file that Claude reads at the start of every session. It captures build commands, conventions, and architecture notes.

Inside the Claude Code session, run:

```
/init
```

Claude will explore the codebase and generate a `CLAUDE.md` file with:
- Build and test commands
- Project structure overview
- Coding conventions it discovers
- Notes on dependencies and tooling

If a `CLAUDE.md` already exists, `/init` will suggest improvements rather than overwriting it.

### Step 2 — Ask Claude About the Project

After `/init`, you can ask open-ended questions directly:

```
What is the overall architecture of this project?
```

```
What are the main entry points and how does data flow through the app?
```

```
Are there any obvious issues or outdated dependencies I should know about?
```

```
How do I run the tests, and where are they located?
```

### Step 3 — Review and Commit CLAUDE.md

Open `CLAUDE.md` and review what Claude generated. Edit anything that is incorrect or missing, then commit it to version control so your whole team benefits:

```bash
git add CLAUDE.md
git commit -m "Add CLAUDE.md for Claude Code project context"
```

### CLAUDE.md Tips

- Keep it under 200 lines — longer files reduce adherence and consume context tokens.
- Be specific: `"Use 2-space indentation with single quotes"` beats `"Format code nicely"`.
- You can create multiple scoped files:
  - `./CLAUDE.md` — project-wide (commit to version control)
  - `./CLAUDE.local.md` — personal overrides (add to `.gitignore`)
  - `~/.claude/CLAUDE.md` — applies to all your projects

---

## 5. Essential Commands Reference

### CLI (run in your terminal)

| Command | Description |
|---|---|
| `claude` | Start an interactive session |
| `claude "describe this project"` | Start with an initial prompt |
| `claude -p "query"` | Non-interactive: run query and exit |
| `claude -c` | Continue the most recent session |
| `claude auth login` | Sign in |
| `claude auth logout` | Sign out |
| `claude auth status` | Show current auth details |
| `claude --version` | Print version |
| `claude update` | Update to the latest version |
| `claude doctor` | Run diagnostics |

### Slash Commands (inside a session)

| Command | Description |
|---|---|
| `/help` | Show all available commands |
| `/init` | Generate or improve CLAUDE.md |
| `/login` | Re-authenticate |
| `/logout` | Sign out |
| `/status` | Show auth, model, and context usage |
| `/memory` | View or edit CLAUDE.md and auto-memory |
| `/config` | Open the settings UI |
| `/permissions` | Manage which tools Claude can use |
| `/clear` | Clear conversation history |
| `/compact` | Compress context to free up space |
| `exit` or `Ctrl+D` | Exit the session |

### Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+C` | Cancel the current operation |
| `Ctrl+D` | Exit the session |
| `Up / Down` | Navigate command history |
| `Shift+Enter` | Insert a newline without submitting |

---

## 6. Troubleshooting by OS

### macOS

**`command not found: claude`**

The installer could not add `~/.local/bin` to your PATH. Fix:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**`dyld: cannot load` or `dyld: Symbol not found`**

Your macOS version is too old (requires 13.0+). Update your OS or use Homebrew.

**Keychain locked / password sync error**

```bash
security unlock-keychain ~/Library/Keychains/login.keychain-db
```

If that fails, open **Keychain Access** app → **Edit** → **Change Password for Keychain "login"**.

---

### Linux

**`command not found: claude`**

Add `~/.local/bin` to your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**`Error loading shared library libstdc++.so.6`**

The binary architecture does not match (glibc vs musl). Check with:

```bash
ldd /bin/ls
```

Then reinstall Claude Code. For Alpine Linux, install `libgcc` and `libstdc++` first (see the Alpine section above).

**`Illegal instruction` on startup**

Your CPU architecture does not match the downloaded binary. Verify:

```bash
uname -m
```

Reinstall and ensure you are running on x64 or ARM64.

**Process `Killed` during install**

Not enough RAM. You need at least 4 GB. Add a swap file or use a larger machine.

---

### Windows

**`'claude' is not recognized as an internal or external command`**

Add Claude Code to your PATH:

1. Open **Start** → search **Environment Variables** → click **Edit the system environment variables**
2. Under **User variables**, select `Path` → **Edit** → **New**
3. Add `%USERPROFILE%\.local\bin`
4. Click OK and restart your terminal

**`Claude Code requires git-bash`**

Install [Git for Windows](https://git-scm.com/downloads/win). If Git Bash is installed in a non-default path, set it explicitly in `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe"
  }
}
```

**`Claude Code does not support 32-bit Windows`**

You ran the x86 version of PowerShell. Use **Windows PowerShell** (64-bit) from the Start menu.

**`syntax error near unexpected token '<'`**

The install script URL returned HTML (likely a regional block or network issue). Try WinGet instead:

```powershell
winget install Anthropic.ClaudeCode
```

**`The token '&&' is not valid`**

You ran a PowerShell command in Command Prompt (CMD). Use the CMD installer instead:

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

**WSL 2: JetBrains IDE not detected**

Add a Windows Firewall inbound rule for port `63342`, or switch to mirrored networking in `.wslconfig`.

---

### Network / Proxy / Firewall (All Platforms)

**Test connectivity:**

```bash
curl -sI https://storage.googleapis.com
```

**Set a proxy:**

```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

**Corporate TLS inspection / custom CA:**

```bash
export NODE_EXTRA_CA_CERTS=/path/to/corporate-ca.pem
```

**Windows TLS 1.2 (if the installer fails with SSL errors):**

```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
irm https://claude.ai/install.ps1 | iex
```

**Update CA certificates on Ubuntu/Debian:**

```bash
sudo apt-get install --reinstall ca-certificates
```

**`503 Service Unavailable`** — Temporary outage. Wait a few minutes and retry.

---

## 7. Common Gotchas

### API Key Overrides Subscription Login

If you have `ANTHROPIC_API_KEY` set in your environment and it is invalid or expired, you will get `403 Forbidden` even with an active subscription.

```bash
unset ANTHROPIC_API_KEY          # macOS / Linux
Remove-Item Env:ANTHROPIC_API_KEY  # Windows PowerShell
```

Then confirm you are using subscription auth:

```
/status
```

---

### CLAUDE.md Instructions Being Ignored

- Run `/memory` inside a session to confirm the file is being loaded.
- Keep CLAUDE.md under 200 lines.
- Make instructions concrete and specific.
- Check for conflicting instructions across multiple CLAUDE.md files (project, local, user-level).

---

### Repeated Permission Prompts

Use `/permissions` inside a session to allowlist tools, or add them to `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(git commit *)",
      "Bash(npm run *)",
      "Read(**/*.ts)"
    ]
  }
}
```

---

### ripgrep Not Working (Code Search Broken)

Install ripgrep for your platform:

```bash
# macOS
brew install ripgrep

# Ubuntu / Debian
sudo apt install ripgrep

# Windows
winget install BurntSushi.ripgrep.MSVC

# Alpine
apk add ripgrep
```

If you installed ripgrep system-wide but Claude Code uses its built-in version, override:

```json
{
  "env": {
    "USE_BUILTIN_RIPGREP": "0"
  }
}
```

---

### High Memory / Context Overflow

If Claude Code slows down or loses track of context:

- Run `/compact` to compress the conversation.
- Start a fresh session (`exit` then `claude`) between unrelated tasks.
- Add large generated or binary directories to `.gitignore` so Claude does not scan them.

---

## Official Documentation

| Topic | URL |
|---|---|
| Installation & system requirements | https://docs.anthropic.com/en/claude-code/setup |
| Quickstart | https://docs.anthropic.com/en/claude-code/quickstart |
| Authentication | https://docs.anthropic.com/en/claude-code/authentication |
| CLAUDE.md and memory | https://docs.anthropic.com/en/claude-code/memory |
| CLI reference | https://docs.anthropic.com/en/claude-code/cli-reference |
| Settings & permissions | https://docs.anthropic.com/en/claude-code/settings |
| Troubleshooting | https://docs.anthropic.com/en/claude-code/troubleshooting |
| Supported countries | https://www.anthropic.com/supported-countries |
| Anthropic Console (API keys) | https://console.anthropic.com |
