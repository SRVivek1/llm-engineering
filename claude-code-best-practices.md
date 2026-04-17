# Claude Code — Best Practices for Agentic Coding

The developer's go-to reference for working effectively with Claude Code. Covers prompting strategy, dos and don'ts, context management, what to do when things go wrong, and how to keep token usage under control.

Official docs: https://docs.anthropic.com/en/claude-code  
Anthropic engineering blog: https://www.anthropic.com/engineering

---

## Table of Contents

1. [The Agentic Coding Mindset](#1-the-agentic-coding-mindset)
2. [Project Setup for AI Collaboration](#2-project-setup-for-ai-collaboration)
3. [Writing Effective Prompts](#3-writing-effective-prompts)
4. [Dos and Don'ts](#4-dos-and-donts)
5. [Managing Context and Token Usage](#5-managing-context-and-token-usage)
6. [When Claude Is Stuck — Recovery Playbook](#6-when-claude-is-stuck--recovery-playbook)
7. [Security and Permissions](#7-security-and-permissions)
8. [Git and Code Review Workflow](#8-git-and-code-review-workflow)
9. [Advanced Productivity Patterns](#9-advanced-productivity-patterns)
10. [Anti-Patterns to Avoid](#10-anti-patterns-to-avoid)
11. [Quick-Reference Cheatsheet](#11-quick-reference-cheatsheet)
12. [Official References](#12-official-references)

---

## 1. The Agentic Coding Mindset

Agentic coding is fundamentally different from using a chatbot. Claude Code is not an autocomplete tool — it reads your codebase, runs commands, edits multiple files, and takes actions. That power requires a different mental model.

### Collaborate, don't dictate

Think of Claude Code as a junior-to-mid-level engineer that has read your entire codebase. It needs:
- Clear goals ("what" and "why")
- Context about constraints (tech stack, style, existing patterns)
- Feedback loops (correct it, it learns within the session)
- Human review before changes are committed

### Trust, but verify

Claude is capable of writing production-quality code, but it can also make plausible-sounding mistakes. Your job is to set direction, review output, and steer when needed — not to simply accept everything it produces.

### Think in tasks, not conversations

An effective agentic session has a clear task boundary. One session, one goal. When you mix unrelated tasks in a single session, context gets polluted and quality degrades.

---

## 2. Project Setup for AI Collaboration

Good setup is the highest-leverage investment. A well-configured project makes every subsequent session faster and more accurate.

### 2.1 Initialize CLAUDE.md with /init

On your first session in any project:

```
/init
```

This generates `CLAUDE.md` — the file Claude reads at the start of every session. Review it, correct anything wrong, and commit it so the whole team benefits.

Reference: https://docs.anthropic.com/en/claude-code/memory

### 2.2 Write a high-quality CLAUDE.md

`CLAUDE.md` is your primary lever for steering Claude across every session. A well-written file is worth more than any single prompt.

**What to include:**

```markdown
# Project Name

## Stack
- Runtime: Node.js 20, TypeScript 5.x
- Frontend: Next.js 14 (App Router), Tailwind CSS
- Backend: tRPC, Drizzle ORM, PostgreSQL
- Testing: Vitest, Playwright

## Build & Dev Commands
- `npm run dev` — start dev server
- `npm run test` — run unit tests
- `npm run test:e2e` — run Playwright tests
- `npm run build` — production build
- `npm run typecheck` — TypeScript type check (no build)

## Code Conventions
- 2-space indentation, single quotes, no semicolons
- Prefer named exports over default exports
- Keep components under 200 lines; extract when larger
- All API routes must validate input with Zod

## Architecture Notes
- Feature folders: src/features/<feature-name>/{components,hooks,api}
- Server Actions live in src/features/<feature-name>/actions.ts
- Database schema: src/db/schema.ts (Drizzle)
- Shared utilities: src/lib/

## Do Not Touch
- src/legacy/ — frozen legacy code, do not modify
- Do not change the database migration files directly
```

**CLAUDE.md rules:**
- Keep it under 200 lines — beyond this, Claude's adherence drops and you consume context tokens
- Be specific over vague: `"Use 2-space indentation"` beats `"Follow our style guide"`
- Update it when the project changes — stale instructions cause confusion

### 2.3 Use scoped CLAUDE.md files

| File | Scope | Commit? |
|---|---|---|
| `./CLAUDE.md` | Project-wide, entire team | Yes |
| `./CLAUDE.local.md` | Your personal overrides | No (add to .gitignore) |
| `~/.claude/CLAUDE.md` | All your projects | N/A |
| `./src/CLAUDE.md` | Scoped to the `src/` subtree | Yes |

Use `CLAUDE.local.md` for preferences that are personal (e.g., "I prefer verbose log output during debugging").

### 2.4 Set up permissions early

Pre-approve commonly used tools so you are not interrupted mid-task:

```json
// ~/.claude/settings.json (user-level, applies to all projects)
{
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git add *)",
      "Bash(npm run *)",
      "Bash(npx *)",
      "Read(**/*)"
    ]
  }
}
```

```json
// .claude/settings.json (project-level, commit this)
{
  "permissions": {
    "allow": [
      "Bash(docker compose *)",
      "Bash(psql *)"
    ]
  }
}
```

Reference: https://docs.anthropic.com/en/claude-code/settings

---

## 3. Writing Effective Prompts

The quality of your prompt determines the quality of Claude's output more than any other single factor.

### 3.1 The anatomy of a good task prompt

A strong prompt answers four questions:

1. **What do you want?** — the specific outcome
2. **Why does it matter?** — the motivation or constraint
3. **What is the current state?** — what already exists
4. **What does success look like?** — how you will know it's done

**Weak prompt:**
```
Fix the auth bug.
```

**Strong prompt:**
```
The login form submits but the user gets a 401 even with correct credentials.
The bug appears only when the email contains uppercase letters — the DB stores
emails as lowercase but the comparison is case-sensitive. Fix the comparison in
src/features/auth/actions.ts and add a test in src/features/auth/actions.test.ts
that covers a mixed-case email login.
```

### 3.2 Give Claude the right level of autonomy

Claude Code has three implicit modes. Use the right one for the job:

| Mode | When to use | How to prompt |
|---|---|---|
| **Ask** | Exploratory, high-stakes, unfamiliar areas | "Explain how X works. Don't change any files yet." |
| **Guided** | Normal feature work | "Implement X. Show me the plan before writing code." |
| **Autonomous** | Routine, well-defined, reversible tasks | "Add validation to all the Zod schemas in src/features/. Commit when done." |

### 3.3 Use examples and references

If you want a specific pattern or style, show it:

```
Add a new endpoint for user profile updates. Follow the exact same pattern as
the existing endpoint in src/features/profile/api/getProfile.ts — same error
handling, same response envelope, same Zod validation approach.
```

### 3.4 Ask Claude to explain before acting

For complex or risky tasks, ask for a plan first:

```
Before writing any code, explain your approach to refactoring the payment module.
List the files you'll touch and any risks I should know about.
```

### 3.5 Iterative refinement beats the perfect prompt

You do not need to write the perfect prompt the first time. Start with a rough goal, review what Claude produces, then steer:

```
That's on the right track, but use React Query instead of useEffect for the fetch.
Also keep the loading state inside the component, not in a context.
```

---

## 4. Dos and Don'ts

### DO

**Commit before every significant task.**
Before asking Claude to refactor a module or fix a bug, `git commit` your current state. This gives you a clean rollback point.

```bash
git add -p && git commit -m "checkpoint before refactor"
```

**Keep sessions focused on one task.**
One session, one goal. When the task is done, start a fresh session for the next one. Mixed-context sessions produce lower-quality output.

**Review every change before accepting.**
Claude edits files autonomously. Read the diff before committing. Check especially: deleted code, changes to shared utilities, any modification to auth/security code.

**Ask Claude to run the tests.**
After implementing a feature or fix, ask:
```
Run the test suite and tell me if anything is broken.
```

**Use /status to stay aware of context size.**
```
/status
```
This shows model, context usage, and remaining tokens. Check it when a session has been running a while.

**Tell Claude when it's wrong.**
If the output is incorrect, say so directly:
```
That's not right — the issue is that the session is expiring on the server side,
not the client. The client token is valid. Focus on the session middleware.
```

**Start fresh sessions for unrelated tasks.**
Exit the current session (`Ctrl+D` or `exit`) and start a new one. Do not carry context from a frontend bug fix into a backend performance task.

**Use headless mode for scripting and CI.**
```bash
claude -p "Run the linter and report any errors" --output-format json
```

Reference: https://docs.anthropic.com/en/claude-code/cli-reference

---

### DON'T

**Don't give vague or open-ended requests for complex tasks.**
"Make this app faster" gives Claude no constraint to work within. It will either do nothing useful or over-reach. Be specific: "The dashboard page takes 4s to load. The bottleneck is the N+1 query in `src/features/dashboard/api.ts:87`. Rewrite it to use a single JOIN."

**Don't approve tool calls without reading them.**
When Claude asks permission to run a command, read it. Approving `rm -rf dist` is fine; approving `rm -rf /` is not. The permission prompt exists for a reason.

**Don't ignore the context warning signs.**
If Claude starts repeating itself, asking you questions it already answered, or producing output that contradicts earlier work — the context window is degrading. Stop and use `/compact` or start fresh.

**Don't pile unrelated tasks in one session.**
If you are fixing a login bug and then ask Claude to "also update the dashboard layout while you're at it," the combined context degrades both tasks. Finish one, then start fresh.

**Don't blindly accept large refactors.**
When Claude touches 10+ files, review the diff carefully. It is easy for a large autonomous change to accidentally delete logic, change function signatures, or break contracts that are not covered by tests.

**Don't put secrets in your prompts.**
Never paste API keys, database connection strings, passwords, or tokens into a prompt. Claude processes these through Anthropic's infrastructure and they will appear in your conversation history.

**Don't fight Claude when it is truly stuck.**
If Claude has failed at the same task 3+ times, it's not a prompt wording issue — something structural is wrong. See [Section 6](#6-when-claude-is-stuck--recovery-playbook).

**Don't use Claude for logic it cannot verify.**
If the correct output requires knowledge Claude doesn't have (e.g., internal company rules, undocumented API behavior), provide that knowledge explicitly in the prompt. Don't expect Claude to infer it.

---

## 5. Managing Context and Token Usage

Context management is the single most important skill for efficient agentic coding. Burning through context means slower responses, degraded quality, and higher costs.

### 5.1 Understanding the context window

Claude has a finite context window — everything in the window (your messages, Claude's responses, file contents, command output) counts toward the limit. When the window fills up:
- Response quality degrades before it hard-limits
- Claude may start contradicting earlier decisions
- Long-running sessions get expensive fast

Check context usage at any time with `/status`.

### 5.2 Use /compact proactively

`/compact` compresses conversation history into a summary, freeing context space without losing the session state.

```
/compact
```

**When to run it:**
- After completing a major subtask within a session
- When `/status` shows you are past 50% context usage
- When Claude starts seeming "forgetful" about earlier decisions

### 5.3 Start fresh sessions for new tasks

When a task is complete, exit and start a new session. Fresh context = faster responses, lower cost, and no carry-over confusion.

```bash
# End current session
exit

# Start new session
claude
```

### 5.4 Keep CLAUDE.md under 200 lines

CLAUDE.md is loaded into every session. A 500-line CLAUDE.md consumes meaningful context before you even type your first prompt.

### 5.5 Avoid pasting large files into the prompt

Instead of pasting a 1,000-line file into the chat, tell Claude where it lives:

```
# Don't do this:
Here is the full contents of src/db/schema.ts: [1000 lines pasted]

# Do this instead:
Look at src/db/schema.ts to understand the table structure.
```

Claude Code can read files directly — it doesn't need you to paste them.

### 5.6 Use .gitignore and .claudeignore to limit scope

Add large generated or binary directories that Claude doesn't need to scan:

```gitignore
# .gitignore (Claude respects these automatically)
node_modules/
.next/
dist/
build/
coverage/
*.min.js
```

For directories that are tracked by git but shouldn't be read by Claude:

```
# .claudeignore
docs/api-snapshots/
test/fixtures/large-data/
```

Reference: https://docs.anthropic.com/en/claude-code/memory#understanding-claudes-memory

### 5.7 Monitor and manage API costs (API key users)

If you are on an API key (not a subscription plan), costs accumulate per token. Strategies to control them:

- Use `/compact` aggressively
- Prefer targeted questions over open-ended exploration
- Use `-p` (headless mode) for one-shot queries — no session overhead
- Use `claude --model claude-haiku-4-5-20251001` for simple tasks (cheaper, faster)
- Reserve Opus/Sonnet for complex architectural decisions

Check the Anthropic Console for usage dashboards: https://console.anthropic.com/usage

### 5.8 Subscription plans and their limits

| Plan | Best for | Limits |
|---|---|---|
| Pro | Individual developers, daily use | Rate-limited, resets periodically |
| Max | Power users, heavy daily use | 5× or 20× higher limits than Pro |
| Team | Development teams | Per-seat, centrally managed |
| Enterprise | Large orgs, compliance requirements | Custom limits, SSO, audit logs |

If you hit a rate limit, the session pauses until the limit resets. Use `/status` to see remaining capacity.

Reference: https://www.anthropic.com/claude/plans

---

## 6. When Claude Is Stuck — Recovery Playbook

When Claude cannot solve a problem after one or two attempts, follow this structured recovery process. Do not retry the same prompt repeatedly — it rarely helps.

### Diagnostic: what type of stuck?

| Symptom | Likely cause |
|---|---|
| Keeps producing the same wrong code | Misunderstood the requirement |
| Writes code that doesn't compile | Missing context about types/interfaces |
| Fixes one thing, breaks another | Context too large / conflicting instructions |
| Says it can't do something that should be possible | Overly conservative safety guardrails |
| Loops or self-contradicts | Context window degrading |
| Good code, wrong behavior at runtime | Bug requires runtime information Claude doesn't have |

---

### 6.1 For stuck features: narrow the scope

If Claude cannot build a feature, break it into the smallest possible step:

```
# Instead of:
Build the full user notification system.

# Try:
Create a single function in src/lib/notifications.ts that takes a userId
and a message string, and inserts one row into the notifications table.
No sending logic, no UI — just the database write.
```

Confirm each small step works before expanding the scope.

### 6.2 Provide the missing context

Claude is stuck because it lacks information. Common missing context:

**Error messages:**
```
Here is the exact error from the browser console:
TypeError: Cannot read properties of undefined (reading 'user')
  at AuthProvider (src/providers/auth.tsx:42:18)
```

**Type definitions:**
```
The User type is defined in src/types/user.ts — read it before making changes.
The API returns this shape: { id: string, email: string, roles: string[] }
```

**Runtime behavior:**
```
The function is called with userId = null when the user is not logged in.
The current code assumes it's always a string, which is the bug.
```

**Expected behavior vs actual behavior:**
```
Expected: form submits → loading spinner shows → success toast appears
Actual: form submits → spinner shows → spinner disappears → nothing else happens
The success toast code is in src/components/Toast.tsx.
```

### 6.3 Ask Claude to explain its understanding first

Before asking Claude to write more code, ask it to explain what it thinks is wrong:

```
Don't write any code yet. Explain in plain language why you think the
authentication is failing and what approach you plan to take to fix it.
```

This surfaces misunderstandings before they turn into wasted code.

### 6.4 Reset the context

If the session has been running long and Claude seems confused or contradictory:

```
/compact
```

Or if `/compact` doesn't help, start fresh:

```bash
exit
claude
```

Then re-state the problem with fresh, clean context. You lose conversation history but gain clarity.

### 6.5 Try a different angle

Some problems have multiple valid approaches. If one is stuck, ask for an alternative:

```
The approach using React context is not working. Let's abandon that.
What is another way to share the auth state between the Header and Sidebar
without using context? Suggest two options and explain the tradeoff.
```

### 6.6 Do it manually, then ask Claude to generalize

For complex bugs, fixing one case by hand and having Claude generalize is faster than asking Claude to figure out everything from scratch:

```
I manually fixed one instance of the bug in src/features/products/api.ts — I added
a null check on line 47 before accessing response.data.items.
Find all other places in the codebase where we access response.data.items without
a null check, and apply the same fix.
```

### 6.7 Provide a reference implementation

If Claude cannot figure out how to implement something, point it to an example:

```
This Stripe webhook handler pattern is from the official Stripe docs — use this
exact pattern (error handling, raw body parsing, signature verification) for our
implementation. Don't invent a different approach.
[paste official code snippet or provide URL]
```

### 6.8 When to escalate out of Claude

Some problems should not be delegated to Claude at all:

- **Flaky tests that only fail in CI** — requires CI environment debugging, not code changes
- **Performance issues with no profiling data** — ask Claude to add instrumentation first, then fix
- **Bugs that require production logs** — get the logs first, then bring them to Claude
- **Architectural decisions with significant trade-offs** — Claude can present options, but you decide
- **Security-critical code** — always have a human expert review auth, cryptography, and access control

---

## 7. Security and Permissions

### 7.1 The permission model

Claude Code asks for permission before running tools. The permission prompt shows exactly what will be executed. Read it. Always.

Types of permissions:
- **Read** — read a file or directory
- **Write/Edit** — modify a file
- **Bash** — execute a shell command
- **Network** — make an external HTTP request (via MCP tools)

Reference: https://docs.anthropic.com/en/claude-code/security

### 7.2 Grant the minimum necessary permissions

The principle of least privilege applies to Claude the same as any other process.

**Good:** Allow specific patterns
```json
"Bash(npm run test:*)"
"Bash(git log --oneline *)"
```

**Risky:** Allow all bash
```json
"Bash(*)"
```

Only grant `Bash(*)` in fully sandboxed, throwaway environments.

### 7.3 Be especially careful with these commands

If Claude asks to run any of the following, read the full command before approving:

- `rm` or `rm -rf` — deletes files, no recycle bin
- `git reset --hard` — discards all local changes permanently
- `git push --force` — can overwrite shared history on remote
- `curl | bash` — executes remote code directly
- `npm install` — installs packages; check what's being installed
- Any command that writes to paths outside the project directory

### 7.4 Never paste secrets into prompts

Claude conversations flow through Anthropic's infrastructure. Never include in prompts:
- API keys or tokens
- Database connection strings
- Passwords or private keys
- PII (names, emails, SSNs) from production data

Use environment variables or reference them by name: "use the `DATABASE_URL` env var."

### 7.5 Use sandboxed mode

Claude Code runs in a sandbox by default on supported platforms. Never disable sandboxing unless you have a specific reason:

```bash
# Don't do this unless you know why:
claude --dangerously-skip-permissions
```

Reference: https://docs.anthropic.com/en/claude-code/security#sandboxing

---

## 8. Git and Code Review Workflow

Integrating Claude Code into a proper Git workflow is essential for safety and team collaboration.

### 8.1 The checkpoint commit pattern

Before any Claude-assisted change, commit the current state:

```bash
git add -A && git commit -m "wip: checkpoint before [task description]"
```

If Claude's output is bad, rollback is instant:

```bash
git reset --hard HEAD~1
```

### 8.2 Review the diff before committing

Never commit Claude's output without reviewing it:

```bash
git diff         # unstaged changes
git diff --staged  # staged changes
```

For large diffs, review file by file:

```bash
git diff src/features/auth/
```

### 8.3 Tell Claude to write atomic commits

Prompt Claude to create meaningful commits, not one giant dump:

```
After implementing each step, create a commit with a descriptive message.
Don't bundle everything into one commit at the end.
```

### 8.4 Use feature branches for AI-assisted work

Work on a branch so you can review, squash, or reset without affecting `main`:

```bash
git checkout -b feat/user-notifications
# do your work with Claude
git log --oneline  # review the commits
git rebase -i main  # clean up before merging
```

### 8.5 Code review checklist for AI-generated code

Before approving a PR that was largely Claude-assisted:

- [ ] Does the code actually solve the stated problem?
- [ ] Are there any files modified that shouldn't be (unrelated changes)?
- [ ] Is any code deleted that was needed elsewhere?
- [ ] Does the change introduce any security issues (auth bypass, SQL injection, XSS)?
- [ ] Are tests added or updated to cover the change?
- [ ] Does the code follow existing project conventions?
- [ ] Are there any TODO comments or debugging artifacts left behind?

---

## 9. Advanced Productivity Patterns

### 9.1 Headless / non-interactive mode

For scripting, CI pipelines, or batch operations:

```bash
# One-shot query and exit
claude -p "What is the total number of TODO comments in this codebase?"

# Pipe output to another tool
claude -p "List all exported functions in src/lib/utils.ts" | grep "async"

# Read from stdin
cat error.log | claude -p "Summarize the errors in this log file"

# JSON output for parsing
claude -p "List all routes" --output-format json
```

Reference: https://docs.anthropic.com/en/claude-code/cli-reference

### 9.2 Multi-Claude patterns (parallel agents)

For large codebases or parallelizable tasks, run multiple Claude sessions simultaneously in separate terminal windows. Each works on a different part of the codebase independently.

**Example: parallel feature development**
```
Terminal 1: claude  →  "Build the backend API for user notifications in src/features/notifications/api/"
Terminal 2: claude  →  "Build the frontend UI for user notifications in src/features/notifications/components/"
```

Merge branches afterward. Each session maintains a clean, focused context.

Reference: https://www.anthropic.com/engineering/claude-code-best-practices

### 9.3 MCP (Model Context Protocol) servers

MCP servers extend Claude Code with new tools: database access, browser control, Slack integration, GitHub integration, and more.

Add an MCP server to a project:

```bash
claude mcp add <server-name> <command>
```

Example — add GitHub MCP:
```bash
claude mcp add github -- npx -y @modelcontextprotocol/server-github
```

Explore available servers: https://modelcontextprotocol.io/directory

### 9.4 IDE integration

Claude Code integrates with VS Code and JetBrains. The IDE integration shows diffs inline and lets you accept/reject individual hunks.

Install the VS Code extension:
```
ext install anthropic.claude-code
```

Reference: https://docs.anthropic.com/en/claude-code/ide-integrations

### 9.5 The /review skill

For quick code review within a session:

```
/review
```

This runs a structured review of the most recent changes and surfaces potential issues.

### 9.6 Automating repetitive tasks with hooks

Claude Code supports hooks — shell commands that fire on events like session start, tool use, or when Claude stops. Configure them in `settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "echo 'Bash tool executed'" }
        ]
      }
    ]
  }
}
```

Common use case: automatically run the linter after Claude edits files, or run tests after every `git commit` call.

Reference: https://docs.anthropic.com/en/claude-code/hooks

---

## 10. Anti-Patterns to Avoid

These are the most common mistakes that reduce Claude Code effectiveness and increase costs.

### The "fix it" loop

**Pattern:** Ask Claude to fix something → Claude produces bad output → ask Claude to fix it again → repeat 5+ times.

**Problem:** You are burning tokens and context on a loop that will not converge because the root cause is a misunderstanding, not a code error.

**Fix:** Stop after 2 failures. Ask Claude to explain its understanding. Identify the misunderstanding and address it directly.

---

### The mega-prompt

**Pattern:** Writing a 500-word prompt that covers every edge case, every constraint, and every preference upfront.

**Problem:** Long prompts are hard to follow perfectly, and getting one detail wrong invalidates the whole output.

**Fix:** Start with the core task. Iterate. Add constraints only when Claude violates them.

---

### The infinite session

**Pattern:** Keeping a single session open all day and accumulating tasks across it.

**Problem:** Context grows, quality degrades, costs increase, and errors from early in the session bleed into later work.

**Fix:** One task per session. `/compact` within long tasks. Exit and start fresh for new tasks.

---

### Context dumping

**Pattern:** Pasting entire files, long error logs, or full API documentation into the prompt.

**Problem:** Wastes context tokens, increases cost, and Claude still may not find the relevant part.

**Fix:** Point Claude to files it can read itself. Paste only the directly relevant section. Summarize long logs.

---

### Over-granting permissions

**Pattern:** Setting `"allow": ["Bash(*)"]` to avoid permission prompts.

**Problem:** Claude can now run any shell command without confirmation. A bad prompt or a hallucinated fix can cause irreversible damage.

**Fix:** Allow specific patterns: `"Bash(npm run *)"`, `"Bash(git status)"`, etc.

---

### Skipping the review

**Pattern:** Letting Claude edit files, stage them, and push without reviewing the diff.

**Problem:** AI-generated code contains mistakes. Unfamiliar patterns can land in production undetected.

**Fix:** `git diff` before every commit. Review every file changed, not just the ones you asked about.

---

### Asking Claude what it cannot know

**Pattern:** "Why is this slow in production?" with no profiling data. "Why did this request fail?" with no server logs.

**Problem:** Claude will hallucinate a plausible-sounding reason because it has no access to runtime information.

**Fix:** Get the data first (profiling output, logs, network traces), then bring it to Claude for analysis.

---

## 11. Quick-Reference Cheatsheet

### Session management

| Action | Command |
|---|---|
| Start a session | `claude` |
| Start with a prompt | `claude "describe this codebase"` |
| Continue last session | `claude -c` |
| One-shot query (no session) | `claude -p "your question"` |
| Check context and auth status | `/status` |
| Compress conversation history | `/compact` |
| Clear conversation, fresh start | `/clear` |
| Exit | `Ctrl+D` or `exit` |

### Context management

| Situation | Action |
|---|---|
| Context at 50%+ | Run `/compact` |
| Claude seems confused | Start a new session |
| CLAUDE.md too long | Trim to under 200 lines |
| Large files in context | Point Claude to them, don't paste |
| Session slow/expensive | Exit and use `-p` for remaining queries |

### When stuck

| Symptom | Recovery |
|---|---|
| Wrong output, same approach | Ask Claude to explain first, then reprompt |
| Compile errors | Share the exact error message |
| Runtime errors | Share the stack trace + call context |
| Circular loop | `/compact` or start fresh |
| Repeated wrong direction | Ask for alternative approach |
| Complex bug | Fix one case manually, ask Claude to generalize |

### Safety

| Risk | Mitigation |
|---|---|
| Bad Claude output | `git commit` before every task |
| Runaway command | Read every Bash permission prompt |
| Secrets in context | Never paste — reference env var names |
| Large autonomous change | Review full `git diff` before committing |
| Security-critical code | Human expert review required |

---

## 12. Official References

| Topic | URL |
|---|---|
| Claude Code overview | https://docs.anthropic.com/en/claude-code |
| Quickstart | https://docs.anthropic.com/en/claude-code/quickstart |
| CLI reference (all flags and commands) | https://docs.anthropic.com/en/claude-code/cli-reference |
| CLAUDE.md and memory system | https://docs.anthropic.com/en/claude-code/memory |
| Settings and permissions | https://docs.anthropic.com/en/claude-code/settings |
| Security and sandboxing | https://docs.anthropic.com/en/claude-code/security |
| Hooks (automation) | https://docs.anthropic.com/en/claude-code/hooks |
| IDE integrations | https://docs.anthropic.com/en/claude-code/ide-integrations |
| MCP servers | https://docs.anthropic.com/en/claude-code/mcp |
| Troubleshooting | https://docs.anthropic.com/en/claude-code/troubleshooting |
| Model Context Protocol directory | https://modelcontextprotocol.io/directory |
| Anthropic engineering blog | https://www.anthropic.com/engineering |
| Claude Code best practices (Anthropic) | https://www.anthropic.com/engineering/claude-code-best-practices |
| Subscription plans | https://www.anthropic.com/claude/plans |
| Supported countries | https://www.anthropic.com/supported-countries |
| Anthropic Console (API keys & usage) | https://console.anthropic.com |
