# Claude Code — CLI Cheat Sheet

Complete reference for every CLI command, flag, slash command, keyboard shortcut, and settings key. Each section includes sample usages and links to official documentation.

Official CLI reference: https://docs.anthropic.com/en/claude-code/cli-reference  
Settings reference: https://docs.anthropic.com/en/claude-code/settings

---

## Table of Contents

1. [Starting a Session](#1-starting-a-session)
2. [CLI Flags — Full Reference](#2-cli-flags--full-reference)
3. [Authentication Commands](#3-authentication-commands)
4. [Output and Format Flags](#4-output-and-format-flags)
5. [Model and Effort Flags](#5-model-and-effort-flags)
6. [Session and Context Flags](#6-session-and-context-flags)
7. [Permission and Security Flags](#7-permission-and-security-flags)
8. [Prompt and System Injection Flags](#8-prompt-and-system-injection-flags)
9. [MCP and Plugin Commands](#9-mcp-and-plugin-commands)
10. [Worktree and Parallel Work](#10-worktree-and-parallel-work)
11. [Automation and Scripting Flags](#11-automation-and-scripting-flags)
12. [Slash Commands (Inside a Session)](#12-slash-commands-inside-a-session)
13. [Keyboard Shortcuts](#13-keyboard-shortcuts)
14. [Settings Reference (settings.json)](#14-settings-reference-settingsjson)
15. [Permission Rules Syntax](#15-permission-rules-syntax)
16. [Hooks — Event Reference](#16-hooks--event-reference)
17. [Environment Variables](#17-environment-variables)
18. [Quick Recipes](#18-quick-recipes)

---

## 1. Starting a Session

Official docs: https://docs.anthropic.com/en/claude-code/quickstart

| Command | What it does |
|---|---|
| `claude` | Open an interactive session in the current directory |
| `claude "describe this project"` | Open a session with an initial prompt pre-filled |
| `claude -p "query"` | Headless / non-interactive: run query and exit |
| `claude -c` | Resume the most recently active session |
| `claude -r "session-name"` | Resume a specific session by name or ID |

**Sample usages:**

```bash
# Start a fresh session in your project
cd ~/projects/my-app && claude

# Start with context — useful when you know what you want immediately
claude "Explain the architecture of this project, focusing on the data layer"

# One-shot query — great for scripting or quick lookups
claude -p "What environment variables does this project require?"

# Resume where you left off yesterday
claude -c

# Resume a specific named session
claude -r "auth-refactor"
claude -r "a1b2c3d4-5678-..."   # by session UUID
```

---

## 2. CLI Flags — Full Reference

Official docs: https://docs.anthropic.com/en/claude-code/cli-reference

### Core Flags

| Flag | Short | Description |
|---|---|---|
| `--print` | `-p` | Headless mode: run query, print response, exit |
| `--continue` | `-c` | Load the most recent conversation and continue |
| `--resume` | `-r` | Resume a session by name or UUID |
| `--version` | `-v` | Print the installed version number |
| `--help` | `-h` | Print help text and exit |
| `--verbose` | | Enable verbose output (detailed internal logging) |
| `--debug` | | Enable debug mode; optionally filter by subsystem |
| `--debug-file` | | Write debug output to a file instead of stdout |
| `--name` | `-n` | Assign a human-readable name to the session |

**Sample usages:**

```bash
# Headless — integrate into scripts, CI, or pipelines
claude -p "List all TODO comments in this codebase"

# Verbose — useful when diagnosing strange behavior
claude --verbose "Run the test suite and explain any failures"

# Debug with subsystem filter
claude --debug "api,mcp" "Why is the MCP server not connecting?"

# Debug output to file (keep terminal clean)
claude --debug --debug-file /tmp/claude-debug.log "query"

# Name a session for easy resuming later
claude -n "payment-module-refactor"
```

---

## 3. Authentication Commands

Official docs: https://docs.anthropic.com/en/claude-code/authentication

| Command | Description |
|---|---|
| `claude auth login` | Sign in with browser OAuth flow |
| `claude auth login --console` | Sign in without opening a browser (copy-paste code) |
| `claude auth logout` | Sign out and remove stored credentials |
| `claude auth status` | Show current authentication status as JSON |
| `claude setup-token` | Generate a long-lived OAuth token (for CI / scripts) |

**Sample usages:**

```bash
# Standard login — opens browser automatically
claude auth login

# Headless login — useful in SSH sessions or remote machines
claude auth login --console

# Check who you're logged in as (also shows remaining quota)
claude auth status

# Generate a 1-year OAuth token for use in CI pipelines
claude setup-token
# Then set in CI: export CLAUDE_CODE_OAUTH_TOKEN=<token>
```

**Authentication precedence** (highest to lowest):
1. Cloud provider env vars (Bedrock, Vertex AI, Foundry)
2. `ANTHROPIC_AUTH_TOKEN`
3. `ANTHROPIC_API_KEY`
4. `CLAUDE_CODE_OAUTH_TOKEN`
5. OAuth subscription login (`/login` flow)

---

## 4. Output and Format Flags

Official docs: https://docs.anthropic.com/en/claude-code/cli-reference#output-formats

| Flag | Values | Description |
|---|---|---|
| `--output-format` | `text`, `json`, `stream-json` | Format of the response |
| `--input-format` | `text`, `stream-json` | Format of piped input |
| `--json-schema` | JSON schema string | Force response to match a schema |
| `--include-partial-messages` | | Include partial streaming events in `stream-json` |
| `--include-hook-events` | | Include hook lifecycle events in `stream-json` output |
| `--replay-user-messages` | | Re-emit user messages for acknowledgment (stream-json only) |

**Sample usages:**

```bash
# Plain text — default, human-readable
claude -p "Summarize this codebase" --output-format text

# JSON — machine-readable, great for piping into jq
claude -p "List all exported functions in src/lib/utils.ts" --output-format json | jq '.result'

# Streaming JSON — for real-time processing in scripts
claude -p "Run the linter and report errors" --output-format stream-json

# Force structured output matching a specific schema
claude -p "Extract all API endpoints" \
  --output-format json \
  --json-schema '{"type":"array","items":{"type":"object","properties":{"method":{"type":"string"},"path":{"type":"string"}}}}'

# Process stdin — pipe files or command output into Claude
cat error.log | claude -p "Classify these errors by severity"
git diff HEAD~1 | claude -p "Write a commit message for these changes"
```

---

## 5. Model and Effort Flags

Official docs: https://docs.anthropic.com/en/claude-code/cli-reference

| Flag | Values | Description |
|---|---|---|
| `--model` | model ID string | Override the model for this session |
| `--effort` | `low`, `medium`, `high`, `xhigh`, `max` | Set reasoning effort level |
| `--fallback-model` | model ID string | Use this model if primary is overloaded |
| `--betas` | comma-separated string | Enable beta API headers |

**Available models (as of April 2026):**

| Model ID | Use case |
|---|---|
| `claude-opus-4-7` | Most capable, complex architectural decisions |
| `claude-sonnet-4-6` | Default — balanced speed and capability |
| `claude-haiku-4-5-20251001` | Fastest and cheapest, simple/routine tasks |

**Sample usages:**

```bash
# Use Haiku for cheap, fast, routine tasks (linting, formatting checks)
claude --model claude-haiku-4-5-20251001 -p "Find all console.log statements"

# Use Opus for complex decisions (architecture, security review)
claude --model claude-opus-4-7 "Design the database schema for a multi-tenant SaaS"

# Max effort for hard problems (slower but more thorough reasoning)
claude --effort max "This algorithm has an off-by-one error I can't find. Debug it."

# Low effort for quick lookups (faster, less compute)
claude --effort low -p "What does the --dry-run flag do in this Makefile?"

# Fallback model if primary is rate-limited
claude -p --model claude-opus-4-7 --fallback-model claude-sonnet-4-6 "query"
```

---

## 6. Session and Context Flags

Official docs: https://docs.anthropic.com/en/claude-code/cli-reference

| Flag | Short | Description |
|---|---|---|
| `--continue` | `-c` | Continue the most recent session |
| `--resume` | `-r` | Resume a session by name or UUID |
| `--session-id` | | Use an explicit session UUID |
| `--name` | `-n` | Name this session |
| `--fork-session` | | Create a new session ID instead of reusing |
| `--no-session-persistence` | | Disable session saving for this run |
| `--from-pr` | | Resume sessions linked to a GitHub PR number |
| `--add-dir` | | Add additional working directories to the session |
| `--max-turns` | | Limit agentic turns (stops after N tool calls) |

**Sample usages:**

```bash
# Continue the most recent session
claude -c

# Resume by name (set with -n when you started it)
claude -r "payment-module-refactor"

# Resume by UUID
claude -r "550e8400-e29b-41d4-a716-446655440000"

# Fork: resume the context of a session but save to a new session ID
claude --resume "feature-work" --fork-session

# Add a sibling package to the working context (monorepos)
claude --add-dir ../packages/shared-ui ../packages/api-client

# Resume session tied to GitHub PR #42
claude --from-pr 42

# Limit turns — safety guard for automated pipelines
claude -p --max-turns 5 "Refactor the auth module"

# One-shot with no session saved (useful for sensitive queries)
claude -p --no-session-persistence "What is in .env.local?"
```

---

## 7. Permission and Security Flags

Official docs: https://docs.anthropic.com/en/claude-code/settings#permission-modes  
Security: https://docs.anthropic.com/en/claude-code/security

| Flag | Values | Description |
|---|---|---|
| `--permission-mode` | `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` | Start in a specific permission mode |
| `--allowedTools` | tool pattern strings | Tools that auto-execute without asking |
| `--disallowedTools` | tool pattern strings | Tools that are never available this session |
| `--tools` | comma-separated tool names | Restrict Claude to only these tools |
| `--dangerously-skip-permissions` | | Skip all permission prompts (use only in sandboxed envs) |
| `--allow-dangerously-skip-permissions` | | Add `bypassPermissions` to the permission mode cycle |

**Permission modes explained:**

| Mode | Behavior |
|---|---|
| `default` | Asks permission for writes, edits, and commands |
| `acceptEdits` | Auto-accepts file edits; still asks for Bash |
| `plan` | Claude proposes a plan; you approve before any action |
| `auto` | Auto mode — Claude decides based on trust context |
| `dontAsk` | Never prompts for permission (trusts all actions) |
| `bypassPermissions` | Skips everything — for fully sandboxed CI use only |

**Sample usages:**

```bash
# Plan mode — see what Claude intends to do before it does anything
claude --permission-mode plan "Refactor the payments module"

# Accept file edits automatically, but still confirm Bash commands
claude --permission-mode acceptEdits "Fix all TypeScript errors"

# Allow only specific tools for a focused task
claude --tools "Read,Glob,Grep" -p "Audit all API endpoints"

# Pre-allow safe read-only git commands
claude --allowedTools "Bash(git log *)" "Bash(git diff *)" "Bash(git status)"

# Block network access for this session
claude --disallowedTools "WebFetch" "WebSearch"

# Fully bypass permissions — ONLY for disposable CI containers
claude -p --dangerously-skip-permissions "Run the full test suite and fix failures"
```

---

## 8. Prompt and System Injection Flags

Official docs: https://docs.anthropic.com/en/claude-code/cli-reference

| Flag | Description |
|---|---|
| `--system-prompt` | Replace the entire system prompt with a custom string |
| `--system-prompt-file` | Load the full system prompt from a file |
| `--append-system-prompt` | Append additional text to the existing system prompt |
| `--append-system-prompt-file` | Append content of a file to the existing system prompt |
| `--bare` | Skip auto-discovery (no CLAUDE.md, no project context) |

**Sample usages:**

```bash
# Override system prompt — use for domain-specific agents
claude --system-prompt "You are a senior Python data engineer. Always use pandas and type hints." \
  "Refactor the ETL pipeline"

# Load system prompt from file — keeps CLI commands clean
claude --system-prompt-file ./prompts/security-reviewer.txt \
  -p "Review this authentication module for vulnerabilities"

# Append extra rules without replacing defaults — useful for adding project rules
claude --append-system-prompt "Always add JSDoc comments to public functions."

# Combine: file-based additions
claude --append-system-prompt-file ./team-conventions.txt "Implement the user profile page"

# Bare mode — no CLAUDE.md loaded, pure model interaction
claude --bare -p "Translate this Python snippet to Go"
```

---

## 9. MCP and Plugin Commands

Official docs: https://docs.anthropic.com/en/claude-code/mcp  
MCP directory: https://modelcontextprotocol.io/directory

### MCP (Model Context Protocol)

| Command | Description |
|---|---|
| `claude mcp add <name> <command>` | Add an MCP server |
| `claude mcp add --transport sse <name> <url>` | Add an SSE-based MCP server |
| `claude mcp list` | List all configured MCP servers |
| `claude mcp remove <name>` | Remove an MCP server |
| `claude mcp get <name>` | Show details for a specific server |
| `claude mcp reset-project-choices` | Reset project-level MCP trust decisions |

**MCP flags:**

| Flag | Description |
|---|---|
| `--mcp-config` | Load MCP servers from a JSON config file |
| `--strict-mcp-config` | Only use MCP servers from `--mcp-config`, ignore all others |

**Sample usages:**

```bash
# Add GitHub MCP — enables PR management, issue tracking from Claude
claude mcp add github -- npx -y @modelcontextprotocol/server-github

# Add a filesystem MCP server scoped to a directory
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /tmp/workspace

# Add Playwright for browser automation
claude mcp add playwright -- npx -y @playwright/mcp@latest

# Add an SSE-based remote MCP server
claude mcp add --transport sse my-remote-server https://mcp.example.com/sse

# Load MCP config from file — useful in team environments
claude --mcp-config ./mcp-servers.json "Test the login flow in the browser"

# Strict mode: ignore all other MCP configs, use only what's specified
claude --strict-mcp-config --mcp-config ./ci-mcp.json -p "Run tests"

# List all servers
claude mcp list
```

### Plugins

| Command | Description |
|---|---|
| `claude plugin install <plugin>` | Install a plugin |
| `claude plugin uninstall <name>` | Remove a plugin |
| `claude plugin list` | List installed plugins |

```bash
# Install a plugin from official marketplace
claude plugin install code-review@claude-plugins-official

# Load plugins from a local directory (development)
claude --plugin-dir ./my-plugins
```

---

## 10. Worktree and Parallel Work

Official docs: https://docs.anthropic.com/en/claude-code/cli-reference#worktrees

Worktrees let Claude work on an isolated Git branch without touching your main working copy. Run multiple Claude sessions in parallel without conflicts.

| Flag | Short | Description |
|---|---|---|
| `--worktree` | `-w` | Start in an isolated git worktree on a new branch |
| `--tmux` | | Create a tmux session for the worktree |
| `--remote` | | Create a web session on claude.ai linked to this task |
| `--remote-control` / `--rc` | | Start a Remote Control server for this session |

**Sample usages:**

```bash
# Start Claude on an isolated branch — safe for large refactors
claude -w feature/add-notifications "Build the push notification system"

# Worktree + tmux — each feature gets its own pane
claude -w feature/auth-redesign --tmux "Redesign the auth flow"
claude -w feature/dashboard --tmux "Rebuild the dashboard with React Query"

# Remote session — run from the web UI while local context stays
claude --remote "Fix the flaky E2E tests"

# Multiple parallel worktrees for independent features
# Terminal 1:
claude -w feature/backend-api "Build the REST API for notifications"
# Terminal 2:
claude -w feature/frontend-ui "Build the React components for notifications"
```

**Worktree settings (in `settings.json`):**

```json
{
  "worktree": {
    "symlinkDirectories": ["node_modules", ".cache"],
    "sparsePaths": ["packages/my-app", "shared/utils"]
  }
}
```

---

## 11. Automation and Scripting Flags

Official docs: https://docs.anthropic.com/en/claude-code/cli-reference

| Flag | Description |
|---|---|
| `--max-budget-usd` | Stop after spending this many USD (API key billing only) |
| `--max-turns` | Limit agentic tool-call cycles |
| `--permission-prompt-tool` | Use an MCP tool to handle permission prompts (for agents) |
| `--exclude-dynamic-system-prompt-sections` | Improve prompt cache reuse in headless runs |
| `--no-session-persistence` | Don't save the session to disk |
| `--init` | Run initialization hooks, then start session |
| `--init-only` | Run initialization hooks, then exit (no session) |
| `--maintenance` | Run maintenance hooks, then start session |

**Sample usages:**

```bash
# Budget cap — prevents runaway costs on API key billing
claude -p --max-budget-usd 2.00 "Refactor all files in src/legacy/"

# Limit turns — safe guard in CI so Claude doesn't loop forever
claude -p --max-turns 10 "Fix all TypeScript compile errors"

# Optimize prompt cache — reduces cost in repeated headless runs
claude -p --exclude-dynamic-system-prompt-sections "Run the test suite"

# Init hooks — run project setup scripts before session starts
claude --init

# CI pipeline: run maintenance checks and exit without starting a session
claude --init-only

# Pipe output to other tools
claude -p --output-format json "List all API routes" | jq '.[].path'

# Read from stdin
git diff HEAD~1 HEAD | claude -p "Write a changelog entry for these changes"

# Compose with other commands
npm test 2>&1 | claude -p --output-format text "These tests failed. Explain why and suggest fixes."
```

---

## 12. Slash Commands (Inside a Session)

Official docs: https://docs.anthropic.com/en/claude-code/slash-commands

Slash commands are typed inside an active Claude Code session.

### Session Management

| Command | Description |
|---|---|
| `/help` | Show all available slash commands |
| `/status` | Show auth, model name, context usage, and remaining tokens |
| `/clear` | Clear the conversation history (keeps CLAUDE.md in context) |
| `/compact` | Compress conversation history to free context space |
| `/compact [instructions]` | Compact with specific summary instructions |
| `exit` or `Ctrl+D` | End the session |

**Sample usages:**

```
/status
# → Model: claude-sonnet-4-6, Context: 34% used, Tokens remaining: ~130k

/compact
# → Compresses history; Claude summarizes what happened so far

/compact Focus on keeping the authentication flow decisions
# → Compact with a custom focus for the summary

/clear
# → Wipes conversation; fresh start in the same terminal window
```

---

### File and Memory

| Command | Description |
|---|---|
| `/init` | Generate or improve CLAUDE.md for the project |
| `/memory` | View and edit CLAUDE.md and auto-memory files |
| `@filename` | Reference a file inline without leaving the prompt |

**Sample usages:**

```
/init
# → Claude scans the codebase and generates CLAUDE.md

/memory
# → Opens CLAUDE.md in your editor for review/editing

What does @src/features/auth/actions.ts do?
# → Claude reads the file as part of answering the question
```

---

### Authentication

| Command | Description |
|---|---|
| `/login` | Re-authenticate (triggers browser OAuth flow) |
| `/logout` | Sign out of current account |

---

### Permissions and Configuration

| Command | Description |
|---|---|
| `/config` | Open the interactive settings UI |
| `/permissions` | View and manage tool permission rules |
| `/doctor` | Run diagnostics on the current environment |

**Sample usages:**

```
/permissions
# → Lists current allow/deny rules; lets you add new ones interactively

/config
# → Opens the settings panel (model, permissions, display options)
```

---

### Modes

| Command | Description |
|---|---|
| `/plan` | Switch to plan mode (propose before acting) |
| `/auto` | Switch to auto mode (trust-based automatic execution) |
| `/fast` | Toggle fast mode (Claude Opus with faster output) |

---

### Review and Quality

| Command | Description |
|---|---|
| `/review` | Run a structured code review on recent changes |
| `/security-review` | Run a security-focused review on recent changes |
| `/init` | (Re-)generate CLAUDE.md |

---

### Custom Slash Commands (Project Commands)

Create `.claude/commands/your-command.md` to add your own slash commands:

```markdown
---
description: Run our full quality pipeline
---

Run the following in order and report any failures:
1. `npm run typecheck`
2. `npm run lint`
3. `npm run test`
4. `npm run build`
```

Then use it in a session:

```
/your-command
```

Reference: https://docs.anthropic.com/en/claude-code/slash-commands#custom-commands

---

## 13. Keyboard Shortcuts

Official docs: https://docs.anthropic.com/en/claude-code/keyboard-shortcuts

### Universal

| Shortcut | Action |
|---|---|
| `Ctrl+C` | Cancel the current running operation |
| `Ctrl+D` | Exit the session (at empty prompt) |
| `Ctrl+L` | Clear the terminal screen |
| `Shift+Enter` | Insert a newline without submitting the prompt |
| `Up / Down` | Navigate through command history |
| `Tab` | Accept autocomplete suggestion |
| `Esc` | Cancel current autocomplete / dismiss popup |

### Multiline Input

| Shortcut | Action |
|---|---|
| `Shift+Enter` | New line without submitting |
| `Ctrl+Enter` | Submit multiline input (alternative to Enter) |

### During Response

| Shortcut | Action |
|---|---|
| `Ctrl+C` | Interrupt Claude mid-response |
| `Esc` | Cancel current tool execution |

### Vim Mode

To enable vim keybindings, add to `~/.claude.json`:

```json
{ "editorMode": "vim" }
```

| Shortcut | Action |
|---|---|
| `Esc` | Enter normal mode |
| `i` | Enter insert mode |
| `v` | Enter visual mode |
| `dd` | Delete current line |
| `yy` / `p` | Yank and paste |
| `/pattern` | Search in the input |

---

## 14. Settings Reference (settings.json)

Official docs: https://docs.anthropic.com/en/claude-code/settings

### Settings file locations and precedence

| File | Scope | Commit to git? |
|---|---|---|
| Managed / system settings | All users on machine (IT-deployed) | N/A |
| `~/.claude/settings.json` | Your account, all projects | No |
| `.claude/settings.json` | This project, all collaborators | Yes |
| `.claude/settings.local.json` | This project, you only | No |

**Precedence:** Managed > CLI flags > Local project > Shared project > User

---

### Essential Settings

```json
{
  "model": "claude-sonnet-4-6",
  "effortLevel": "high",
  "language": "english",
  "includeGitInstructions": true,
  "permissions": {
    "allow": ["Bash(git *)", "Bash(npm run *)", "Read(**/*.ts)"],
    "ask": ["Bash(git push *)", "Bash(npm publish *)"],
    "deny": ["WebFetch", "Read(./.env)"]
  },
  "env": {
    "NODE_ENV": "development",
    "USE_BUILTIN_RIPGREP": "0"
  }
}
```

---

### All Settings Keys

| Key | Type | Description |
|---|---|---|
| `model` | string | Override the default model |
| `effortLevel` | `low` \| `medium` \| `high` \| `xhigh` | Persist effort level across sessions |
| `language` | string | Claude's preferred response language (e.g. `"japanese"`) |
| `includeGitInstructions` | boolean | Include git workflow context (default: `true`) |
| `alwaysThinkingEnabled` | boolean | Enable extended thinking by default |
| `autoUpdatesChannel` | `stable` \| `latest` | Release channel for auto-updates |
| `minimumVersion` | string | Prevent downgrade below this version |
| `cleanupPeriodDays` | number | Delete session files older than N days (default: `30`) |
| `outputStyle` | string | Configure response style (e.g. `"Explanatory"`) |
| `viewMode` | `default` \| `verbose` \| `focus` | Default transcript view |
| `tui` | `default` \| `fullscreen` | Terminal UI renderer |
| `defaultShell` | `bash` \| `powershell` | Shell for `!` commands |
| `prefersReducedMotion` | boolean | Reduce UI animations |
| `spinnerTipsEnabled` | boolean | Show tips in spinner (default: `true`) |
| `showClearContextOnPlanAccept` | boolean | Offer "clear context" when accepting a plan |
| `showThinkingSummaries` | boolean | Show extended thinking summaries |
| `feedbackSurveyRate` | number | Probability of survey (0–1); `0` to disable |
| `autoMemoryDirectory` | string | Custom directory for auto-memory files |
| `plansDirectory` | string | Where plan files are stored |
| `apiKeyHelper` | string | Script that outputs a dynamic API key/token |
| `attribution.commit` | string | Custom text for Claude Code git attribution |
| `attribution.pr` | string | Custom text for Claude Code PR attribution |
| `hooks` | object | Lifecycle hooks config (see Section 16) |
| `env` | object | Env vars injected into every session |
| `permissions` | object | Allow / deny / ask rules (see Section 15) |
| `sandbox` | object | Sandbox filesystem/network configuration |
| `worktree` | object | Worktree symlink and sparse-checkout config |

**Global config** (`~/.claude.json`):

| Key | Description |
|---|---|
| `editorMode` | Keybinding mode: `"normal"` or `"vim"` |
| `autoScrollEnabled` | Follow new output in fullscreen mode (default: `true`) |
| `autoConnectIde` | Auto-connect to IDE on startup (default: `false`) |
| `autoInstallIdeExtension` | Auto-install IDE extension (default: `true`) |
| `showTurnDuration` | Show how long each turn took (default: `true`) |
| `terminalProgressBarEnabled` | Show terminal progress bar (default: `true`) |
| `teammateMode` | Agent display mode: `auto`, `in-process`, `tmux` |

---

## 15. Permission Rules Syntax

Official docs: https://docs.anthropic.com/en/claude-code/settings#permission-rules

Permission rules appear in `allow`, `ask`, and `deny` arrays inside `"permissions"`.

### Rule syntax

| Pattern | Matches |
|---|---|
| `Bash` | Any Bash command |
| `Read` | Any file read |
| `Edit` | Any file edit |
| `Write` | Any file write |
| `WebFetch` | Any web fetch |
| `WebSearch` | Any web search |
| `Bash(npm run *)` | Bash commands starting with `npm run ` |
| `Bash(git log *)` | Bash commands starting with `git log ` |
| `Read(./.env)` | Reading exactly `./.env` |
| `Read(./src/**)` | Reading any file under `./src/` |
| `WebFetch(domain:api.example.com)` | Fetches to `api.example.com` only |
| `Edit\|Write` | Either Edit or Write |

### Full example

```json
{
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(npm run *)",
      "Bash(npx *)",
      "Bash(docker compose up *)",
      "Bash(docker compose down)",
      "Read(**/*)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(npm publish *)",
      "Bash(docker build *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl * | bash)",
      "Read(./.env)",
      "Read(./.env.local)",
      "WebFetch"
    ]
  }
}
```

### Sandbox settings (for fine-grained OS-level control)

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": ["/tmp/build", "~/.kube"],
      "denyRead": ["~/.aws/credentials", "~/.ssh/"]
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org", "registry.npmjs.org"],
      "allowUnixSockets": ["/var/run/docker.sock"],
      "allowLocalBinding": true
    }
  }
}
```

---

## 16. Hooks — Event Reference

Official docs: https://docs.anthropic.com/en/claude-code/hooks

Hooks are shell commands (or HTTP calls) that fire automatically on lifecycle events.

### All hook events

| Event | When it fires |
|---|---|
| `SessionStart` | Session begins or resumes |
| `SessionEnd` | Session terminates |
| `UserPromptSubmit` | Before Claude processes your message |
| `PreToolUse` | Before a tool call executes |
| `PostToolUse` | After a tool call succeeds |
| `PostToolUseFailure` | After a tool call fails |
| `PermissionRequest` | When a permission dialog appears |
| `PermissionDenied` | When auto mode denies a tool |
| `Stop` | Claude finishes responding (end of turn) |
| `StopFailure` | Turn ends due to API error |
| `PreCompact` | Before context compaction |
| `PostCompact` | After context compaction |
| `SubagentStart` | Subagent is spawned |
| `SubagentStop` | Subagent finishes |
| `TaskCreated` | Task created via TaskCreate |
| `TaskCompleted` | Task marked completed |
| `Notification` | Claude sends a notification |
| `InstructionsLoaded` | CLAUDE.md or rules loaded |
| `ConfigChange` | Config file changes mid-session |
| `CwdChanged` | Working directory changes |
| `FileChanged` | A watched file changes |
| `WorktreeCreate` | Worktree being created |
| `WorktreeRemove` | Worktree being removed |
| `Elicitation` | MCP server requests user input |
| `ElicitationResult` | User responds to MCP elicitation |
| `TeammateIdle` | Teammate agent about to go idle |

### Hook handler types

| Type | What it does |
|---|---|
| `command` | Runs a shell command; receives JSON on stdin |
| `http` | Sends JSON as an HTTP POST request |
| `prompt` | Sends a prompt to Claude for evaluation |
| `agent` | Spawns a Claude subagent |

### Example hooks

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npm run lint -- --fix",
            "async": true,
            "statusMessage": "Auto-fixing lint issues..."
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "~/.claude/hooks/confirm-rm.sh",
            "statusMessage": "Checking rm safety..."
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "terminal-notifier -message 'Claude is done' -title 'Claude Code'",
            "async": true
          }
        ]
      }
    ]
  }
}
```

**Hook exit codes:**

| Exit code | Meaning |
|---|---|
| `0` | Success; Claude reads stdout for JSON output |
| `2` | Blocking error; stderr is fed back to Claude as context |
| Other | Non-blocking error; first line of stderr shown to user |

---

## 17. Environment Variables

Official docs: https://docs.anthropic.com/en/claude-code/settings#environment-variables

### Authentication

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | API key from the Anthropic Console |
| `ANTHROPIC_AUTH_TOKEN` | Alternative auth token |
| `CLAUDE_CODE_OAUTH_TOKEN` | Long-lived OAuth token (from `claude setup-token`) |

### Provider overrides (for enterprise cloud deployments)

| Variable | Description |
|---|---|
| `CLAUDE_CODE_USE_BEDROCK=1` | Route requests through Amazon Bedrock |
| `CLAUDE_CODE_USE_VERTEX=1` | Route requests through Google Vertex AI |
| `CLAUDE_CODE_USE_FOUNDRY=1` | Route requests through Microsoft Azure Foundry |
| `ANTHROPIC_MODEL` | Override the default model |
| `ANTHROPIC_SMALL_FAST_MODEL` | Model to use for lightweight background tasks |

### Proxy and TLS

| Variable | Description |
|---|---|
| `HTTP_PROXY` | HTTP proxy URL |
| `HTTPS_PROXY` | HTTPS proxy URL |
| `NODE_EXTRA_CA_CERTS` | Path to corporate CA certificate bundle |

### Behavior overrides

| Variable | Description |
|---|---|
| `USE_BUILTIN_RIPGREP=0` | Use system-installed ripgrep instead of bundled |
| `CLAUDE_CODE_GIT_BASH_PATH` | Path to Git Bash on Windows (non-default install) |
| `DISABLE_AUTOUPDATER=1` | Disable automatic updates |
| `DISABLE_ERROR_REPORTING=1` | Disable crash/error reporting to Anthropic |
| `DISABLE_NON_ESSENTIAL_TRAFFIC=1` | Disable telemetry and non-essential network calls |

### Setting env vars per-project (settings.json)

```json
{
  "env": {
    "NODE_ENV": "development",
    "DATABASE_URL": "postgresql://localhost:5432/myapp_dev",
    "USE_BUILTIN_RIPGREP": "0"
  }
}
```

---

## 18. Quick Recipes

Practical one-liners and patterns for common developer workflows.

### Codebase exploration

```bash
# Understand a new project quickly
claude "Explain the overall architecture, main entry points, and data flow of this project"

# Find all places a function is used
claude -p "Find all callers of the processPayment() function and explain each use case"

# Audit dependencies
claude -p "List all third-party dependencies, their versions, and what they're used for"

# Find all API endpoints
claude -p --output-format json "List all REST/GraphQL endpoints defined in this codebase"
```

### Code review and quality

```bash
# Review staged changes before committing
git diff --staged | claude -p "Review these changes for bugs, security issues, and style problems"

# Write a commit message
git diff --staged | claude -p "Write a concise, conventional commit message for these changes"

# Review a PR diff
git diff main...HEAD | claude -p "Summarize what this PR does and flag any concerns"

# Find security issues
claude -p "Audit this codebase for common security vulnerabilities: SQL injection, XSS, insecure secrets, missing auth checks"
```

### Debugging

```bash
# Diagnose a failing test
npm test 2>&1 | claude -p "These tests are failing. Explain the root cause and how to fix it."

# Analyze an error log
cat production.log | claude -p "Identify the most critical errors and their likely causes"

# Debug a build failure
npm run build 2>&1 | claude -p "The build is failing. What is wrong and how do I fix it?"
```

### Automation

```bash
# Generate changelog from git log
git log --oneline v1.0.0..HEAD | claude -p "Generate a user-facing changelog from these commits"

# Document a module
claude -p "Write JSDoc comments for all exported functions in src/lib/payments.ts"

# Translate comments/docs to another language
claude --system-prompt "Respond only in Japanese" -p "Translate the comments in src/utils.ts to Japanese"

# CI quality gate
claude -p --max-turns 5 --max-budget-usd 1.00 \
  "Run the linter and tests. If anything fails, fix it automatically. Report what you changed."
```

### Context-efficient patterns

```bash
# Use Haiku for cheap, fast, read-only tasks
claude --model claude-haiku-4-5-20251001 -p "Count the number of TODO comments in this codebase"

# Compact then continue when context is high
# Inside a session:
# /compact
# Then continue with your next task

# Fresh session for each task (best practice)
claude -n "add-email-validation" "Add email validation to the registration form"
# ... task done, exit ...
claude -n "fix-logout-bug" "The logout button doesn't clear the session cookie"
```

### Team and CI integration

```bash
# Pre-commit hook: auto-review before every commit
# .git/hooks/pre-commit
#!/bin/bash
git diff --staged | claude -p --output-format text \
  "Review these changes. If there are bugs or security issues, list them and exit with code 1. Otherwise exit 0."

# GitHub Actions: auto-review PR
- name: Claude Code Review
  run: |
    git diff origin/main...HEAD | \
    claude -p --output-format json \
      "Review this PR diff. Return JSON: {passed: bool, issues: string[]}"
```

---

## Official References

| Topic | URL |
|---|---|
| CLI reference (all flags) | https://docs.anthropic.com/en/claude-code/cli-reference |
| Quickstart | https://docs.anthropic.com/en/claude-code/quickstart |
| Settings and permissions | https://docs.anthropic.com/en/claude-code/settings |
| Authentication | https://docs.anthropic.com/en/claude-code/authentication |
| Slash commands | https://docs.anthropic.com/en/claude-code/slash-commands |
| Security and sandboxing | https://docs.anthropic.com/en/claude-code/security |
| Hooks (automation) | https://docs.anthropic.com/en/claude-code/hooks |
| MCP servers | https://docs.anthropic.com/en/claude-code/mcp |
| IDE integrations | https://docs.anthropic.com/en/claude-code/ide-integrations |
| Worktrees | https://docs.anthropic.com/en/claude-code/cli-reference#worktrees |
| CLAUDE.md and memory | https://docs.anthropic.com/en/claude-code/memory |
| Troubleshooting | https://docs.anthropic.com/en/claude-code/troubleshooting |
| Model Context Protocol directory | https://modelcontextprotocol.io/directory |
| Anthropic Console (API keys & billing) | https://console.anthropic.com |
| Subscription plans | https://www.anthropic.com/claude/plans |
| Supported countries | https://www.anthropic.com/supported-countries |
