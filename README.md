# AgentGateway Docker Setup

This repository contains a Docker setup for AgentGateway with OpenAI and Anthropic providers configured.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (get from [OpenAI Platform](https://platform.openai.com/api-keys))
- Anthropic API key (get from [Anthropic Console](https://console.anthropic.com/settings/keys))

## Quick Start

1. **Clone or navigate to this directory**

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=sk-your-actual-openai-key
   ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key
   ```

3. **Build and start all services**
   ```bash
   docker-compose up -d --build
   ```

   This starts:
   - AgentGateway (port 3000)
   - UI Dashboard (port 15000)
   - Jaeger tracing (port 16686)
   - Hello Agent (port 9001)
   - Calculator Agent (port 9002)

4. **Check the logs**
   ```bash
   docker-compose logs -f
   ```

5. **Access the services**
   - Gateway API: http://localhost:3000
   - UI Dashboard: http://localhost:15000
   - Metrics: http://localhost:15020/metrics
   - Jaeger UI (Tracing): http://localhost:16686

## Usage

### OpenAI Requests

Send requests to the OpenAI provider via the `/openai` prefix:

```bash
curl -X POST http://localhost:3000/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Anthropic Requests

#### Native Messages Format (Recommended for Claude)

```bash
curl -X POST http://localhost:3000/anthropic/v1/messages \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```


### MCP Server Requests

#### MCP Stdio Connection

Connect to MCP servers running via standard input/output. The example configuration uses the `@modelcontextprotocol/server-everything` package:

```bash
# List available tools from the MCP server
curl -X POST http://localhost:3000/mcp/stdio \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

The stdio connection automatically manages the lifecycle of the MCP server process.

#### MCP HTTP Connection

Connect to MCP servers running on HTTP endpoints. First, start your MCP server on port 3005:

```bash
# Example: Start an MCP server (adjust based on your server implementation)
# node your-mcp-server.js --port 3005
```

Then connect through AgentGateway:

```bash
# List available tools from the HTTP MCP server
curl -X POST http://localhost:3000/mcp/http \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

Access the MCP UI at http://localhost:15000/ui/ to interactively explore and test MCP tools.

For detailed examples and testing instructions, see [MCP_EXAMPLES.md](./MCP_EXAMPLES.md).

### A2A Agent Requests

AgentGateway supports the Agent-to-Agent (A2A) protocol, enabling communication between agentic applications.

#### Discover Agent Capabilities

Get an agent's card to see its available skills:

```bash
# Hello Agent card
curl http://localhost:3000/agent/hello/.well-known/agent.json

# Calculator Agent card
curl http://localhost:3000/agent/calculator/.well-known/agent.json
```

#### Execute Agent Tasks

**Hello Agent - Greeting:**
```bash
curl -X POST http://localhost:3000/agent/hello/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "greet",
    "parameters": {
      "name": "Alice",
      "language": "english"
    }
  }'
```

**Calculator Agent - Calculation:**
```bash
curl -X POST http://localhost:3000/agent/calculator/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "calculate",
    "parameters": {
      "operation": "add",
      "a": 15,
      "b": 27
    }
  }'
```

For complete A2A agent setup and examples, see [agents/README.md](./agents/README.md).

## Observability

This setup includes comprehensive observability features for monitoring MCP server interactions:

### Metrics

Prometheus-compatible metrics are exposed at http://localhost:15020/metrics.

**Key Metrics:**
- `list_calls_total`: Total number of tool calls, labeled by server name and tool name
- Request latency, error rates, and throughput metrics

Access metrics:
```bash
curl http://localhost:15020/metrics
```

Example output:
```
list_calls_total{server="everything",tool="echo"} 5
list_calls_total{server="everything",tool="add"} 3
```

### Distributed Tracing

Jaeger distributed tracing is enabled via OpenTelemetry. Access the Jaeger UI at http://localhost:16686.

**Features:**
- View end-to-end request traces for MCP tool calls
- Inspect operation timing and dependencies
- Debug performance issues and bottlenecks
- Filter traces by service, operation, or tags

**Example Operations:**
- `call_tool`: Traces individual tool executions with full context
- `initialize`: Connection initialization traces
- `tools/list`: Tool discovery traces

### Logging

AgentGateway automatically logs all requests to stdout. View logs with:

```bash
docker-compose logs -f agentgateway
```

Logs include:
- Session IDs
- Request types (initialize, tools/list, tools/call)
- Tool names and arguments
- Response status and timing
- Error details

### Monitoring MCP Traffic

1. **Real-time Metrics**: Monitor tool usage patterns
   ```bash
   watch -n 1 'curl -s http://localhost:15020/metrics | grep list_calls_total'
   ```

2. **Trace Analysis**: Use Jaeger to identify slow operations
   - Open http://localhost:16686
   - Select "agentgateway" service
   - Search for traces by operation name or time range

3. **Log Analysis**: Filter logs for specific tools or errors
   ```bash
   docker-compose logs agentgateway | grep "tool_name"
   ```

## Configuration

The `agentgateway.yaml` file contains the gateway configuration:

- **Telemetry**:
  - OpenTelemetry endpoint: `http://jaeger:4317`
  - Random sampling enabled for distributed tracing

- **Routes**:
  - `/openai/*` - Routes to OpenAI provider
  - `/anthropic/*` - Routes to Anthropic provider
  - `/mcp/stdio/*` - Routes to MCP servers via stdio
  - `/mcp/http/*` - Routes to MCP servers via HTTP
  - `/agent/hello/*` - Routes to Hello A2A agent
  - `/agent/calculator/*` - Routes to Calculator A2A agent

- **Policies**:
  - CORS enabled for all origins (including MCP-specific headers)
  - Backend authentication using environment variables
  - A2A protocol support for agent-to-agent communication

- **Providers**:
  - OpenAI: Supports chat completions and models endpoints
  - Anthropic: Supports both native messages format and OpenAI-compatible format
  - MCP: Supports both stdio and HTTP connection methods for MCP tool servers
  - A2A: Agent-to-agent protocol for communication between agentic applications

## Management Commands

```bash
# Start the gateway
docker-compose up -d

# Stop the gateway
docker-compose down

# View logs
docker-compose logs -f agentgateway

# Restart the gateway
docker-compose restart

# Rebuild after configuration changes
docker-compose up -d --build
```

## Health Check

Check if the gateway is running:

```bash
curl http://localhost:3000/health
```

## Using with Claude Code

To use AgentGateway with Claude Code:

```bash
export ANTHROPIC_BASE_URL="http://localhost:3000/anthropic"
```

This routes all Claude Code traffic through AgentGateway while maintaining full compatibility.

## MCP Server Configuration

### Stdio Connection

The stdio connection runs MCP servers as child processes. The configuration in `agentgateway.yaml` includes:

```yaml
- name: mcp-stdio-backend
  target:
    mcp:
      targets:
        - name: everything
          stdio:
            cmd: npx
            args:
              - "-y"
              - "@modelcontextprotocol/server-everything"
```

**Key Points:**
- Uses `npx -y` to automatically install and run the MCP server package
- Server lifecycle is managed by AgentGateway
- No need to manually start/stop the MCP server
- Perfect for development and testing

### HTTP Connection

The HTTP connection connects to MCP servers running as separate HTTP services:

```yaml
- name: mcp-http-backend
  target:
    mcp:
      targets:
        - name: mcp-http-server
          http:
            host: http://localhost:3005/mcp/
```

**Key Points:**
- Requires the MCP server to be running separately on the specified port
- Better for production deployments
- Allows MCP servers to be scaled independently
- Supports load balancing and high availability

### Adding Custom MCP Servers

To add your own MCP server:

1. **For Stdio**: Update the `args` in the stdio backend configuration to point to your MCP server command
2. **For HTTP**: Start your MCP server on a specific port and update the `host` in the HTTP backend configuration

Example custom stdio server:
```yaml
- name: my-custom-mcp
  target:
    mcp:
      targets:
        - name: custom-server
          stdio:
            cmd: node
            args:
              - "/path/to/your/mcp-server.js"
```

## A2A Agent Configuration

### What is A2A?

A2A (Agent-to-Agent) is an open protocol developed by Google that enables communication and interoperability between agentic applications. It allows agents to:

- Discover capabilities of other agents via agent cards
- Execute tasks with structured parameters
- Collaborate securely without exposing internal systems
- Operate independently with standardized interfaces

### Running the Demo Agents

The demo includes two example A2A agents that run automatically with Docker Compose:

- **Hello Agent**: Runs on port 9001 (accessible via `/agent/hello`)
- **Calculator Agent**: Runs on port 9002 (accessible via `/agent/calculator`)

Both agents start automatically when you run `docker-compose up -d --build`.

**Test the agents:**
```bash
# Get agent card
curl http://localhost:3000/agent/hello/.well-known/agent.json

# Execute a task
curl -X POST http://localhost:3000/agent/hello/task \
  -H "Content-Type: application/json" \
  -d '{"skill": "greet", "parameters": {"name": "World"}}'
```

### Agent Card Structure

Each A2A agent exposes its capabilities via an agent card at `/.well-known/agent.json`:

```json
{
  "name": "Agent Name",
  "version": "1.0.0",
  "description": "Agent description",
  "capabilities": {
    "streaming": false,
    "interactive": true
  },
  "skills": [
    {
      "name": "skill-name",
      "description": "What the skill does",
      "parameters": {
        "type": "object",
        "properties": {
          "param": {
            "type": "string",
            "description": "Parameter description"
          }
        }
      }
    }
  ]
}
```

### Adding Custom A2A Agents

To add your own A2A agent:

1. **Create your agent** with required endpoints:
   - `GET /.well-known/agent.json` - Agent card
   - `POST /task` - Task execution endpoint

2. **Add route in agentgateway.yaml:**
```yaml
routes:
  - name: my-agent-route
    match:
      prefix: /agent/myagent
    policies:
      - cors
      - a2a
    backends:
      - my-agent-backend
```

3. **Add backend configuration:**
```yaml
backends:
  - name: my-agent-backend
    target:
      host: localhost:9003
```

4. **Restart AgentGateway** to apply changes

See [agents/README.md](./agents/README.md) for complete implementation examples.

## Customization

### Changing Default Models

Edit `agentgateway.yaml` and uncomment the model lines:

```yaml
backends:
  - name: openai-backend
    target:
      ai:
        provider:
          openAI:
            model: gpt-4  # Set your preferred model
```

### Adding More Routes

Add additional routes in the `routes` section of `agentgateway.yaml` to support more providers or custom routing logic.

## Troubleshooting

1. **Container won't start**: Check logs with `docker-compose logs`
2. **API key errors**: Verify your `.env` file has valid API keys
3. **Connection refused**: Ensure ports 3000 and 15000 are not in use
4. **Health check failing**: Wait a few seconds for the service to fully initialize

## Documentation

- [AgentGateway Quickstart](https://agentgateway.dev/docs/quickstart/)
- [OpenAI Provider](https://agentgateway.dev/docs/llm/providers/openai/)
- [Anthropic Provider](https://agentgateway.dev/docs/llm/providers/anthropic/)
- [MCP Server Connections](https://agentgateway.dev/docs/mcp/connect/)
  - [Stdio Connection](https://agentgateway.dev/docs/mcp/connect/stdio/)
  - [HTTP Connection](https://agentgateway.dev/docs/mcp/connect/http/)
- [MCP Observability](https://agentgateway.dev/docs/mcp/mcp-observability/)
- [A2A Agent Protocol](https://agentgateway.dev/docs/agent/about/)
  - [Connecting to A2A Agents](https://agentgateway.dev/docs/agent/a2a/)
