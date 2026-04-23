# MCP Server Guide: Zero to Expert

## Table of Contents

1. [What is MCP?](#1-what-is-mcp)
2. [How MCP Works](#2-how-mcp-works)
3. [Core Protocol Specification](#3-core-protocol-specification)
4. [Transport Mechanisms](#4-transport-mechanisms)
5. [Finding Existing MCP Servers](#5-finding-existing-mcp-servers)
6. [Building Your First MCP Server](#6-building-your-first-mcp-server)
7. [Advanced Server Patterns](#7-advanced-server-patterns)
8. [Real-World Use Cases](#8-real-world-use-cases)
9. [Integrating MCP with LLM Platforms](#9-integrating-mcp-with-llm-platforms)
10. [Security Considerations](#10-security-considerations)
11. [Requirements and Dependencies](#11-requirements-and-dependencies)
12. [Quick Reference](#12-quick-reference)

---

## 1. What is MCP?

**Model Context Protocol (MCP)** is an open standard that enables AI applications to securely connect to external tools, data sources, and services. Think of it as a "USB-C port for AI" — a universal plug that lets any LLM application talk to any external system using a single, consistent interface.

### The Problem MCP Solves

Before MCP, every AI application needed custom integrations for every tool it wanted to use:

```
Without MCP:
  Claude ──── custom code ──── GitHub
  Claude ──── custom code ──── Slack
  Claude ──── custom code ──── Database
  GPT   ──── different code ── GitHub
  GPT   ──── different code ── Slack

With MCP:
  Claude ──┐
  GPT    ──┤── MCP Protocol ── GitHub MCP Server
  Cursor ──┘                ── Slack MCP Server
                            ── Database MCP Server
```

### Who Created MCP?

MCP was created and open-sourced by **Anthropic** (makers of Claude) in late 2024. It is now maintained as an open standard with community contributions via Specification Enhancement Proposals (SEPs).

### Key Concepts at a Glance

| Term | Meaning |
|------|---------|
| **MCP Host** | The AI application (Claude Desktop, Claude Code, VS Code, Cursor) |
| **MCP Client** | The protocol client embedded in the host |
| **MCP Server** | An external program that exposes tools/data via MCP |
| **Tool** | A function an LLM can call (e.g., `search_github`, `query_database`) |
| **Resource** | Data a server can provide (e.g., file contents, API responses) |
| **Prompt** | Reusable template interactions exposed by a server |

---

## 2. How MCP Works

### Architecture Overview

```
┌──────────────────────────────────────────┐
│           MCP Host                       │
│  (Claude Code / Claude Desktop / Cursor) │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │        MCP Client Manager        │    │
│  │  (manages multiple connections)  │    │
│  └──────┬───────────┬─────────│─────┘    │
└─────────┼───────────┼────────────────────┘
          │           │
    ┌─────▼──┐   ┌────▼───┐
    │ Client │   │ Client │   ... (one per server)
    └─────┬──┘   └────┬───┘
          │           │
   ┌──────▼──┐  ┌─────▼───┐
   │ Stdio   │  │  HTTP   │   Transport Layer
   └──────┬──┘  └─────┬───┘
          │           │
   ┌──────▼──┐  ┌─────▼────────────────────────────┐
   │ Weather │  │ GitHub MCP Server │  MCP Servers │
   │  Server │  └──────────────────────────────────┘
   └─────────┘
```

### The Conversation Flow

1. **Initialization**: Client sends `initialize` with protocol version and capabilities
2. **Negotiation**: Server responds with its supported capabilities
3. **Discovery**: Client calls `tools/list` to learn what tools are available
4. **LLM Decides**: User prompt goes to LLM → LLM decides to use a tool
5. **Execution**: Client calls `tools/call` with arguments → server executes → returns result
6. **Response**: Result goes back to LLM → LLM incorporates into its response

### Example Interaction

```
User: "What are the open GitHub issues in my repo?"

LLM thinks: I can use the github_list_issues tool

MCP Call:
  tools/call {
    name: "github_list_issues",
    arguments: { repo: "myuser/myrepo", state: "open" }
  }

Server returns:
  [{ title: "Fix login bug", number: 42 }, ...]

LLM: "You have 3 open issues: #42 Fix login bug, ..."
```

---

## 3. Core Protocol Specification

MCP uses **JSON-RPC 2.0** as its message format. Every message is a JSON object with a method name and parameters.

### Server Primitives

#### Tools

Tools are functions the LLM can call. Each tool has:
- `name`: Unique identifier
- `title`: Human-readable name
- `description`: What the tool does (critical — LLM reads this)
- `inputSchema`: JSON Schema describing expected arguments

```json
{
  "name": "search_files",
  "title": "Search Files",
  "description": "Search for files by content or name. Use this when the user wants to find specific code or text.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Search term" },
      "path": { "type": "string", "description": "Directory to search in" }
    },
    "required": ["query"]
  }
}
```

**Protocol messages**:
- `tools/list` — Get all available tools
- `tools/call` — Execute a tool

#### Resources

Resources are data sources the server can provide. Think of them as read-only data streams.

```json
{
  "uri": "file:///logs/app.log",
  "name": "Application Logs",
  "mimeType": "text/plain"
}
```

**Protocol messages**:
- `resources/list` — List available resources
- `resources/read` — Fetch resource content

#### Prompts

Prompts are reusable interaction templates the server exposes.

```json
{
  "name": "analyze_error",
  "description": "Analyze an error and suggest fixes",
  "arguments": [
    { "name": "error_message", "required": true }
  ]
}
```

**Protocol messages**:
- `prompts/list` — Discover available prompts
- `prompts/get` — Retrieve prompt template

### Client Primitives

Clients can also expose capabilities to servers:

- **Sampling**: Servers can request LLM completions (`sampling/complete`)
- **Elicitation**: Servers can request user input (`elicitation/request`)
- **Logging**: Servers can send log messages to the client

### Notifications

One-way messages (no response expected):
- `tools/list_changed` — Tool list has been updated
- `resources/list_changed` — Resource list has changed
- `prompts/list_changed` — Prompt list has changed

---

## 4. Transport Mechanisms

MCP supports three transport types. Choose based on where the server runs.

### Stdio Transport

Best for **local processes** running on the same machine.

```
Host Process ←──stdin/stdout──→ Server Process
```

**When to use**: Local tools, local databases, scripts on your machine

**Key rules**:
- Server reads JSON-RPC from `stdin`, writes to `stdout`
- Use `stderr` for logs — writing to `stdout` breaks the protocol
- Host starts the server process and manages its lifecycle

**Configuration example** (Claude Desktop):
```json
{
  "mcpServers": {
    "my-tool": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": { "API_KEY": "secret" }
    }
  }
}
```

### Streamable HTTP Transport

Best for **remote servers** accessible over the network.

```
Host ──HTTP POST──→ Server
Host ←──SSE/HTTP──── Server (streaming responses)
```

**When to use**: Cloud services, SaaS integrations, shared team servers

**Features**:
- Multiple concurrent clients supported
- Standard HTTP authentication (Bearer tokens, API keys)
- Automatic reconnection (up to 5 attempts with exponential backoff)
- Works over public internet

**Configuration example** (Claude Code):
```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

### SSE Transport (Deprecated)

Server-Sent Events — still supported but being phased out. Prefer Streamable HTTP for new servers.

---

## 5. Finding Existing MCP Servers

### Official Sources

**Anthropic MCP Registry** (official, curated):
```
https://api.anthropic.com/mcp-registry/
```

**Official GitHub Repository** (reference implementations):
```
https://github.com/modelcontextprotocol/servers
```

### Popular Production-Ready Servers

| Server | What It Does | Transport |
|--------|-------------|-----------|
| **GitHub** | Manage repos, issues, PRs | HTTP |
| **Sentry** | Query errors and stack traces | HTTP |
| **Notion** | Read/write pages and databases | HTTP |
| **Slack** | Send messages, read channels | HTTP |
| **PostgreSQL** | Query and manage databases | stdio |
| **Gmail** | Read/compose emails | HTTP |
| **Figma** | Access design files and assets | HTTP |
| **Asana** | Manage tasks and projects | HTTP |
| **Stripe** | Payment processing data | HTTP |
| **Jira** | Issue tracking | HTTP |
| **Airtable** | Database/spreadsheet operations | HTTP |
| **AWS** | Cloud infrastructure management | HTTP |

### Community Sources

- **GitHub**: Search `"mcp server"` — thousands of community servers
- **NPM**: Packages prefixed with `@mcp/` or `mcp-server-`
- **PyPI**: Python packages with `mcp-` prefix
- **Cursor Directory**: cursor.directory/mcp
- **Glama**: glama.ai/mcp

### Evaluating a Server

Before using a community MCP server, check:
1. Is it open source? Can you audit the code?
2. What permissions/scopes does it request?
3. Is it actively maintained? Recent commits?
4. Does it have clear documentation of what data it accesses?

---

## 6. Building Your First MCP Server

### Python Server (Recommended for Beginners)

#### Setup

```bash
# Create project
mkdir my-mcp-server && cd my-mcp-server
python -m venv venv
source venv/bin/activate

# Install SDK
pip install mcp>=1.2.0 httpx
```

#### Minimal Working Server

```python
# server.py
from mcp.server.fastmcp import FastMCP

# Initialize with server name
mcp = FastMCP("my-tools")


@mcp.tool()
async def add_numbers(a: float, b: float) -> str:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number
    """
    result = a + b
    return f"The sum of {a} + {b} = {result}"


@mcp.tool()
async def get_weather(city: str) -> str:
    """Get current weather for a city.

    Args:
        city: City name (e.g., 'London', 'New York')
    """
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://wttr.in/{city}?format=3"
        )
        return resp.text


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

#### Add Resources

```python
@mcp.resource("file://config")
async def get_config() -> str:
    """Returns the current application configuration."""
    return open("config.json").read()
```

#### Add Prompts

```python
@mcp.prompt()
async def debug_error(error_message: str) -> str:
    """Template for analyzing and debugging errors."""
    return f"""Please analyze this error and suggest a fix:

Error: {error_message}

Provide:
1. Root cause analysis
2. Step-by-step fix
3. How to prevent it in future
"""
```

#### Error Handling Best Practice

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import McpError, ErrorCode

mcp = FastMCP("my-tools")


@mcp.tool()
async def fetch_data(url: str) -> str:
    """Fetch data from a URL.

    Args:
        url: The URL to fetch
    """
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            return resp.text
    except httpx.HTTPError as e:
        raise McpError(ErrorCode.INTERNAL_ERROR, f"HTTP error: {e}")
    except Exception as e:
        raise McpError(ErrorCode.INTERNAL_ERROR, str(e))
```

### TypeScript Server

#### Setup

```bash
mkdir my-mcp-server && cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node ts-node
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true
  }
}
```

#### Minimal Working Server

```typescript
// src/server.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "my-tools",
  version: "1.0.0",
});

// Register a tool
server.registerTool(
  "add_numbers",
  {
    description: "Add two numbers together",
    inputSchema: {
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    },
  },
  async ({ a, b }) => {
    const result = a + b;
    return {
      content: [{ type: "text", text: `${a} + ${b} = ${result}` }],
    };
  }
);

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
```

#### HTTP Server (for Remote Deployment)

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";
import { z } from "zod";

const app = express();
app.use(express.json());

const server = new McpServer({ name: "my-tools", version: "1.0.0" });

server.registerTool("hello", {
  description: "Say hello",
  inputSchema: { name: z.string() },
}, async ({ name }) => ({
  content: [{ type: "text", text: `Hello, ${name}!` }],
}));

app.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport({ req, res });
  await server.connect(transport);
});

app.listen(3000, () => console.log("MCP server on port 3000"));
```

### Testing Your Server

#### Using MCP Inspector

```bash
# Install and run inspector (no install needed)
npx -y @modelcontextprotocol/inspector@latest

# Then connect to your server
# For stdio: select "stdio" and set command to "python server.py"
# For HTTP: select "http" and set URL
```

The inspector provides a web UI to:
- Browse available tools, resources, prompts
- Call tools and see raw JSON-RPC messages
- Debug connection issues

#### Command-Line Testing

```bash
# Test your server directly
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{}}}' | python server.py
```

---

## 7. Advanced Server Patterns

### Dynamic Tool Registration

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dynamic-tools")

# Load tools from config at startup
def register_tools_from_config(config: dict):
    for tool_def in config["tools"]:
        def make_handler(definition):
            async def handler(**kwargs):
                return await call_api(definition["endpoint"], kwargs)
            handler.__doc__ = definition["description"]
            return handler
        
        mcp.add_tool(
            make_handler(tool_def),
            name=tool_def["name"],
            description=tool_def["description"]
        )
```

### Authentication Middleware (HTTP Server)

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.auth import BearerAuthProvider

mcp = FastMCP(
    "secure-tools",
    auth=BearerAuthProvider(token="your-secret-token")
)
```

### Rate Limiting

```python
import time
from collections import defaultdict
from mcp.server.fastmcp import FastMCP
from mcp.types import McpError, ErrorCode

mcp = FastMCP("rate-limited")
call_counts = defaultdict(list)


def check_rate_limit(tool_name: str, max_calls: int = 10, window: int = 60):
    now = time.time()
    calls = call_counts[tool_name]
    calls[:] = [t for t in calls if now - t < window]
    if len(calls) >= max_calls:
        raise McpError(ErrorCode.INTERNAL_ERROR, "Rate limit exceeded")
    calls.append(now)


@mcp.tool()
async def expensive_api_call(query: str) -> str:
    """Call an expensive external API.
    
    Args:
        query: Search query
    """
    check_rate_limit("expensive_api_call")
    # ... actual implementation
    return "result"
```

### Streaming Responses

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("streaming")


@mcp.tool()
async def long_running_task(ctx: Context, steps: int) -> str:
    """Run a task with progress updates.
    
    Args:
        steps: Number of steps to process
    """
    for i in range(steps):
        await ctx.report_progress(i, steps, f"Processing step {i+1}/{steps}")
        # Do actual work here
    
    return f"Completed {steps} steps"
```

---

## 8. Real-World Use Cases

### Developer Workflow Automation

**Scenario**: Debug production errors end-to-end

```
User: "Find the top 3 errors from Sentry this week and create GitHub issues for them"

MCP Chain:
  1. sentry:get_errors(time_range="7d", limit=3)
  2. For each error:
     github:create_issue(title=error.title, body=error.stack_trace)
  3. slack:send_message(channel="#bugs", text="Created 3 issues...")
```

**MCP Servers needed**: Sentry, GitHub, Slack

---

### Database-Driven Development

**Scenario**: Generate API endpoints from database schema

```
User: "Look at our PostgreSQL schema and generate FastAPI endpoints for the users table"

MCP Chain:
  1. postgres:query("SELECT * FROM information_schema.columns WHERE table_name='users'")
  2. LLM generates FastAPI code based on schema
  3. filesystem:write_file("api/users.py", generated_code)
```

**MCP Servers needed**: PostgreSQL, Filesystem

---

### Content Pipeline

**Scenario**: Research → Draft → Publish workflow

```
User: "Research MCP protocol, write a blog post, and save it to Notion"

MCP Chain:
  1. web_search:search("MCP protocol 2025 updates")
  2. LLM writes blog post draft
  3. notion:create_page(title="MCP Guide", content=draft)
  4. notion:add_to_database(database_id="blog-posts", page_id=new_page.id)
```

**MCP Servers needed**: Web Search, Notion

---

### Infrastructure Management

**Scenario**: Auto-remediation of production issues

```
User: "Check if any EC2 instances are over 90% CPU and restart the ones that are"

MCP Chain:
  1. aws:get_ec2_metrics(metric="CPUUtilization", threshold=90)
  2. For each over-threshold instance:
     aws:restart_instance(instance_id=id)
  3. datadog:create_event("Restarted N instances due to high CPU")
```

**MCP Servers needed**: AWS, Datadog

---

### Design-to-Code

**Scenario**: Implement UI from Figma design

```
User: "Implement the login page from our Figma file as a React component"

MCP Chain:
  1. figma:get_component(file_id="abc", node_id="login-page")
  2. LLM analyzes design specs (colors, fonts, layout)
  3. LLM generates React component
  4. filesystem:write_file("src/components/LoginPage.tsx", code)
```

**MCP Servers needed**: Figma, Filesystem

---

## 9. Integrating MCP with LLM Platforms

### Claude Code (CLI)

```bash
# Add HTTP server
claude mcp add --transport http github https://api.githubcopilot.com/mcp/

# Add stdio server
claude mcp add --transport stdio postgres -- npx @bytebase/dbhub

# Add with auth headers
claude mcp add --transport http notion https://api.notion.com/mcp/ \
  --header "Authorization: Bearer YOUR_TOKEN"

# Add with environment variables
claude mcp add --transport stdio mydb \
  --env DB_URL=postgresql://localhost/mydb \
  -- python /path/to/db-server.py

# Manage
claude mcp list
claude mcp get github
claude mcp remove github
```

**Configuration scopes**:

| Scope | Flag | File | Use case |
|-------|------|------|----------|
| Local | (default) | `~/.claude.json` | Personal, private |
| Project | `--scope project` | `.mcp.json` | Shared with team via git |
| User | `--scope user` | `~/.claude.json` | All projects, private |

### Claude Desktop

Add to `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`):

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["@bytebase/dbhub"],
      "env": {
        "DATABASE_URL": "postgresql://localhost/mydb"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
      }
    }
  }
}
```

### Claude API (Programmatic)

```python
import anthropic

client = anthropic.Anthropic()

# Use MCP tool in API call
response = client.beta.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    tools=[{
        "type": "mcp",
        "server_label": "github",
        "server_url": "https://api.githubcopilot.com/mcp/",
        "authorization_token": "ghp_..."
    }],
    messages=[{
        "role": "user",
        "content": "List open issues in myrepo"
    }]
)
```

### Agent SDK (Python)

```python
from anthropic import Anthropic
from anthropic.types.beta.agents import AgentConfig, MCPServerConfig

client = Anthropic()

agent = client.beta.agents.create(
    model="claude-opus-4-7",
    name="DevOps Assistant",
    mcp_servers=[
        MCPServerConfig(
            type="http",
            url="https://api.githubcopilot.com/mcp/",
            authorization_token="ghp_...",
            label="github"
        ),
        MCPServerConfig(
            type="stdio",
            command="python",
            args=["/path/to/postgres-server.py"],
            env={"DB_URL": "postgresql://localhost/mydb"},
            label="postgres"
        )
    ]
)
```

### VS Code / Cursor

Add to workspace settings (`.vscode/settings.json`):

```json
{
  "mcp.servers": {
    "github": {
      "transport": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${env:GITHUB_TOKEN}"
      }
    }
  }
}
```

### Project-Level Sharing (.mcp.json)

Check this file into your repository so the whole team gets the same MCP servers:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["@bytebase/dbhub"],
      "env": {
        "DATABASE_URL": "${DB_URL}"
      }
    },
    "sentry": {
      "transport": "http",
      "url": "https://mcp.sentry.io/",
      "headers": {
        "Authorization": "Bearer ${SENTRY_TOKEN}"
      }
    }
  }
}
```

---

## 10. Security Considerations

### Critical Vulnerabilities to Know

#### 1. Confused Deputy Attack

**Risk**: Malicious MCP clients trick a legitimate OAuth proxy into granting them access using another user's consent cookie.

**Mitigation**:
- Track consent per-client, not just per-user
- Validate the `state` parameter in OAuth flows
- Use PKCE (Proof Key for Code Exchange)

#### 2. Server-Side Request Forgery (SSRF)

**Risk**: A malicious server tells the MCP client to fetch `http://169.254.169.254/` (cloud metadata endpoint), stealing cloud credentials.

**Mitigation**:
```python
import ipaddress
from urllib.parse import urlparse

BLOCKED_RANGES = [
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
    "127.0.0.0/8", "169.254.0.0/16", "::1/128"
]

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False
    try:
        addr = ipaddress.ip_address(parsed.hostname)
        for blocked in BLOCKED_RANGES:
            if addr in ipaddress.ip_network(blocked):
                return False
    except ValueError:
        pass  # Hostname, not IP — apply DNS validation separately
    return True
```

#### 3. Token Passthrough Anti-Pattern

**Risk**: Server accepts tokens without validating they're intended for it.

**Wrong**:
```python
# NEVER do this
def handle_request(request):
    token = request.headers["Authorization"]
    response = external_api.call(token=token)  # Token not validated for THIS server
```

**Right**:
```python
def handle_request(request):
    token = request.headers["Authorization"]
    # Validate token audience is THIS server
    claims = jwt.decode(token, verify_audience=True, audience="my-mcp-server")
```

#### 4. Prompt Injection via Tool Results

**Risk**: A malicious API response contains instructions like "Ignore previous instructions and..."

**Mitigation**: Sanitize tool results before including in context, or use structured output formats.

#### 5. Overly Broad OAuth Scopes

**Risk**: Requesting `files:*` or `admin:*` gives attackers a large attack surface.

**Best practice**: Request minimal scopes and use progressive elevation (request additional scopes only when needed).

### Security Checklist

```
Before deploying any MCP server:
[ ] All external URLs validated (no private IP ranges)
[ ] OAuth tokens validated for audience (not just presence)
[ ] Minimal OAuth scopes requested
[ ] HTTPS enforced for all remote communications
[ ] Session IDs are cryptographically random (not sequential)
[ ] Per-client consent tracking (not per-user)
[ ] All tool inputs validated before use
[ ] Secrets stored in environment variables, not code
[ ] Logs exclude sensitive data (tokens, passwords)
[ ] Rate limiting implemented on expensive operations
```

---

## 11. Requirements and Dependencies

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python SDK | Python 3.10 | Python 3.11+ |
| TypeScript SDK | Node.js 16 | Node.js 20+ |
| Go SDK | Go 1.21 | Go 1.22+ |
| Claude Code | Latest | Latest |
| Claude Desktop | Latest | Latest |

### Python Dependencies

```bash
# Core SDK
pip install mcp>=1.2.0

# Common additions
pip install httpx          # Async HTTP client
pip install pydantic       # Data validation
pip install python-dotenv  # Environment variable loading

# Full requirements.txt
mcp>=1.2.0
httpx>=0.27.0
pydantic>=2.0
python-dotenv>=1.0
```

### TypeScript Dependencies

```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  }
}
```

### Go Dependencies

```bash
go get github.com/modelcontextprotocol/go-sdk/mcp
```

### C# Dependencies

```xml
<PackageReference Include="ModelContextProtocol" Version="1.0.0" />
```

### Available SDKs

| Language | Tier | Stability |
|----------|------|-----------|
| TypeScript | 1 | Stable, production-ready |
| Python | 1 | Stable, production-ready |
| C# | 1 | Stable, production-ready |
| Go | 1 | Stable, production-ready |
| Java | 2 | Supported |
| Rust | 2 | Supported |
| Swift | 3 | Community |
| Ruby | 3 | Community |
| PHP | 3 | Community |
| Kotlin | TBD | In development |

---

## 12. Quick Reference

### Starting a New Python MCP Server

```bash
# 1. Setup
mkdir my-server && cd my-server
python -m venv venv && source venv/bin/activate
pip install mcp httpx

# 2. Create server.py (see section 6)

# 3. Test with inspector
npx -y @modelcontextprotocol/inspector@latest

# 4. Register with Claude Code
claude mcp add --transport stdio my-server -- python /path/to/server.py
```

### Starting a New TypeScript MCP Server

```bash
# 1. Setup
mkdir my-server && cd my-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node

# 2. Create src/server.ts (see section 6)

# 3. Build and run
npx tsc && node dist/server.js

# 4. Test
npx -y @modelcontextprotocol/inspector@latest
```

### Claude Code MCP Commands

```bash
# Add servers
claude mcp add --transport http <name> <url>
claude mcp add --transport stdio <name> -- <command> [args...]
claude mcp add --transport sse <name> <url>          # deprecated

# With authentication
claude mcp add --transport http <name> <url> --header "Authorization: Bearer TOKEN"

# Manage
claude mcp list                    # List all servers
claude mcp get <name>              # Server details
claude mcp remove <name>           # Remove server

# In Claude Code session
/mcp                               # Authenticate / manage MCP
```

### MCP Protocol Methods

```
Lifecycle:
  initialize          Handshake + capability negotiation
  ping                Keep-alive check

Tools:
  tools/list          Get available tools
  tools/call          Execute a tool

Resources:
  resources/list      List available resources
  resources/read      Fetch resource content
  resources/subscribe Subscribe to resource changes

Prompts:
  prompts/list        List available prompts
  prompts/get         Get prompt template

Sampling (client-side):
  sampling/complete   Request LLM completion
```

### Common Pitfalls

| Mistake | Problem | Fix |
|---------|---------|-----|
| Writing to stdout in stdio server | Corrupts JSON-RPC | Use stderr for logs |
| Weak tool descriptions | LLM doesn't know when to use tool | Write clear, specific descriptions |
| Not handling errors | Crashes server | Wrap handlers in try-catch |
| Storing secrets in code | Security leak | Use environment variables |
| No input validation | Crashes or injection | Validate with JSON Schema / Zod |
| Blocking I/O in handlers | Slow responses | Use async/await |

---

## Key Resources

| Resource | URL |
|----------|-----|
| Official Docs | https://modelcontextprotocol.io |
| MCP Specification | https://modelcontextprotocol.io/specification |
| MCP Registry | https://api.anthropic.com/mcp-registry |
| GitHub (servers) | https://github.com/modelcontextprotocol/servers |
| Python SDK | https://github.com/modelcontextprotocol/python-sdk |
| TypeScript SDK | https://github.com/modelcontextprotocol/typescript-sdk |
| MCP Inspector | `npx @modelcontextprotocol/inspector@latest` |
| Claude API Docs | https://docs.anthropic.com/en/docs/agents-and-tools/mcp |
| Claude Code Docs | https://docs.anthropic.com/en/docs/claude-code/mcp |
