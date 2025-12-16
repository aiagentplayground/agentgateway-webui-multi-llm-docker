# AgentGateway Testing Guide

This guide provides commands to test all LLM providers, MCP servers, and A2A agents configured in your AgentGateway setup.

## Prerequisites

- Ensure all containers are running: `docker-compose ps`
- Make sure your API keys are set in `.env` file
- AgentGateway should be accessible at http://localhost:3000

## Architecture Overview

This demo showcases two ways to access AI providers through AgentGateway:

### 1. Unified Gateway (Port 3000)
All providers accessible through a single port with path-based routing:
- **Anthropic**: `http://localhost:3000/anthropic/...`
- **OpenAI**: `http://localhost:3000/openai/...`
- **xAI**: `http://localhost:3000/xai/...`
- **Gemini**: `http://localhost:3000/gemini/...`
- **MCP**: `http://localhost:3000/mcp`
- **A2A Agents**: `http://localhost:3000/agent/...`

### 2. Dedicated Listeners (Ports 3001-3006)
Each provider has its own dedicated port for direct access:
- **Port 3001**: Anthropic Claude only
- **Port 3002**: OpenAI GPT only
- **Port 3003**: xAI Grok only
- **Port 3004**: Google Gemini only
- **Port 3005**: MCP Tools only
- **Port 3006**: A2A Agents only

Both approaches provide the same functionality, rate limiting, and security controls!

## 🎨 Web UI - Interactive Testing

For a user-friendly testing experience, access the Web UI at:

### **http://localhost:8080**

The Web UI provides:
- ✨ Interactive chat interface for all LLM providers (Anthropic, OpenAI, xAI, Gemini)
- 🔧 MCP tool testing interface with dropdown menus
- 🤖 A2A agent interaction forms (Hello & Calculator agents)
- 💅 Beautiful, responsive design with real-time responses
- 🚀 Perfect for demos and manual testing - no curl commands needed!

Simply open your browser and start testing all providers through a clean interface!

---

## 1. Anthropic (Claude)

### List Available Models

```bash
curl -s http://localhost:3000/anthropic/v1/models | jq '.data[] | {id: .id, name: .display_name}'
```

### Chat Completion (Messages API)

```bash
curl -X POST http://localhost:3000/anthropic/v1/messages \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 100,
    "messages": [
      {
        "role": "user",
        "content": "Explain what AgentGateway does in one sentence."
      }
    ]
  }' | jq '.'
```

### Verify Rate Limiting

Run this command 15 times quickly to trigger rate limiting (limit is 10 requests per minute):

```bash
for i in {1..15}; do
  echo "Request $i:"
  curl -s -w "\nHTTP Status: %{http_code}\n" \
    -X POST http://localhost:3000/anthropic/v1/messages \
    -H "Content-Type: application/json" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-haiku-4-5-20251001",
      "max_tokens": 10,
      "messages": [{"role": "user", "content": "Hi"}]
    }' | head -1
  echo "---"
done
```

Expected: First 10 succeed, remaining 5 return 429 (Too Many Requests)

### Using Dedicated Listener (Port 3001)

Access Anthropic directly without path prefix:

```bash
curl -X POST http://localhost:3001/v1/messages \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 100,
    "messages": [
      {
        "role": "user",
        "content": "What is AgentGateway?"
      }
    ]
  }' | jq '.'
```

---

## 2. OpenAI

### List Available Models

```bash
curl -s http://localhost:3000/openai/v1/models | jq '.data[] | {id: .id}'
```

### Chat Completion

```bash
curl -X POST http://localhost:3000/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "user",
        "content": "Write a haiku about API gateways"
      }
    ],
    "max_completion_tokens": 100
  }' | jq '.'
```

### Streaming Response

```bash
curl -X POST http://localhost:3000/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "user",
        "content": "Count from 1 to 5"
      }
    ],
    "stream": true
  }'
```

### With System Message

```bash
curl -X POST http://localhost:3000/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant that always responds in rhymes."
      },
      {
        "role": "user",
        "content": "What is the weather like?"
      }
    ]
  }' | jq '.choices[0].message'
```

### Using Dedicated Listener (Port 3002)

Access OpenAI directly without path prefix:

```bash
curl -X POST http://localhost:3002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "user",
        "content": "Explain AgentGateway in one sentence"
      }
    ],
    "max_completion_tokens": 100
  }' | jq '.'
```

---

## 3. Grok (xAI)

**Note:** Requires `XAI_API_KEY` in your `.env` file

### Chat Completion

```bash
curl -X POST http://localhost:3000/xai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4-1-fast-reasoning",
    "messages": [
      {
        "role": "user",
        "content": "Explain quantum computing in simple terms"
      }
    ],
    "max_completion_tokens": 150
  }' | jq '.'
```

### Test Reasoning Capabilities

```bash
curl -X POST http://localhost:3000/xai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4-1-fast-reasoning",
    "messages": [
      {
        "role": "user",
        "content": "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?"
      }
    ]
  }' | jq '.choices[0].message.content'
```

### List Models

```bash
curl -s http://localhost:3000/xai/v1/models | jq '.'
```

### Using Dedicated Listener (Port 3003)

Access xAI directly without path prefix:

```bash
curl -X POST http://localhost:3003/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4-1-fast-reasoning",
    "messages": [
      {
        "role": "user",
        "content": "What is the speed of light?"
      }
    ],
    "max_completion_tokens": 100
  }' | jq '.'
```

---

## 4. Gemini (Google AI)

**Note:** Requires `GEMINI_API_KEY` in your `.env` file

### List Available Models

```bash
curl -s http://localhost:3000/gemini/v1/models | jq '.data[] | {id: .id}'
```

### Chat Completion

```bash
curl -X POST http://localhost:3000/gemini/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro-preview",
    "messages": [
      {
        "role": "user",
        "content": "Explain the concept of neural networks in simple terms"
      }
    ],
    "max_tokens": 150
  }' | jq '.'
```

### Streaming Response

```bash
curl -X POST http://localhost:3000/gemini/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro-preview",
    "messages": [
      {
        "role": "user",
        "content": "Count from 1 to 5"
      }
    ],
    "stream": true
  }'
```

### Multi-turn Conversation

```bash
curl -X POST http://localhost:3000/gemini/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "",
    "messages": [
      {
        "role": "user",
        "content": "What is the capital of France?"
      },
      {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      {
        "role": "user",
        "content": "What is the population?"
      }
    ]
  }' | jq '.choices[0].message.content'
```

### Using Dedicated Listener (Port 3004)

Access Gemini directly without path prefix:

```bash
curl -X POST http://localhost:3004/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro-preview",
    "messages": [
      {
        "role": "user",
        "content": "What is artificial intelligence?"
      }
    ],
    "max_tokens": 100
  }' | jq '.'
```

---

## 5. MCP Server (Model Context Protocol)

### List Available Tools

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' | jq '.result.tools[] | {name: .name, description: .description}'
```

### Initialize MCP Connection

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }' | jq '.'
```

### Call Echo Tool

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "echo",
      "arguments": {
        "message": "Hello from AgentGateway!"
      }
    }
  }' | jq '.'
```

### Using Dedicated Listener (Port 3005)

Access MCP directly without path prefix:

```bash
curl -X POST http://localhost:3005/ \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' | jq '.result.tools[] | {name: .name, description: .description}'
```

---

## 6. A2A Agents

### Hello Agent

**Get Agent Card:**
```bash
curl -s http://localhost:3000/agent/hello/.well-known/agent.json | jq '.'
```

**List Available Skills:**
```bash
curl -s http://localhost:3000/agent/hello/.well-known/agent.json | jq '.skills[] | {name: .name, description: .description}'
```

**Greet in English:**
```bash
curl -X POST http://localhost:3000/agent/hello/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "greet",
    "parameters": {
      "name": "Alice",
      "language": "english"
    }
  }' | jq '.'
```

**Greet in Spanish:**
```bash
curl -X POST http://localhost:3000/agent/hello/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "greet",
    "parameters": {
      "name": "Carlos",
      "language": "spanish"
    }
  }' | jq '.'
```

**Greet in French:**
```bash
curl -X POST http://localhost:3000/agent/hello/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "greet",
    "parameters": {
      "name": "Marie",
      "language": "french"
    }
  }' | jq '.'
```

**Get Introduction:**
```bash
curl -X POST http://localhost:3000/agent/hello/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "introduce",
    "parameters": {}
  }' | jq '.output.text'
```

### Calculator Agent

**Get Agent Card:**
```bash
curl -s http://localhost:3000/agent/calculator/.well-known/agent.json | jq '.'
```

**List Available Skills:**
```bash
curl -s http://localhost:3000/agent/calculator/.well-known/agent.json | jq '.skills[] | {name: .name, description: .description}'
```

**Addition:**
```bash
curl -X POST http://localhost:3000/agent/calculator/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "calculate",
    "parameters": {
      "operation": "add",
      "a": 42,
      "b": 58
    }
  }' | jq '.'
```

**Multiplication:**
```bash
curl -X POST http://localhost:3000/agent/calculator/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "calculate",
    "parameters": {
      "operation": "multiply",
      "a": 12,
      "b": 8
    }
  }' | jq '.'
```

**Division:**
```bash
curl -X POST http://localhost:3000/agent/calculator/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "calculate",
    "parameters": {
      "operation": "divide",
      "a": 100,
      "b": 4
    }
  }' | jq '.'
```

**Power:**
```bash
curl -X POST http://localhost:3000/agent/calculator/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "power",
    "parameters": {
      "base": 2,
      "exponent": 10
    }
  }' | jq '.'
```

**Square Root:**
```bash
curl -X POST http://localhost:3000/agent/calculator/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "sqrt",
    "parameters": {
      "number": 144
    }
  }' | jq '.'
```

### Using Dedicated Listener (Port 3006)

Access A2A agents directly with simplified paths:

**Hello Agent:**
```bash
# Get agent card
curl -s http://localhost:3006/hello/.well-known/agent.json | jq '.'

# Greet
curl -X POST http://localhost:3006/hello/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "greet",
    "parameters": {
      "name": "Demo User",
      "language": "english"
    }
  }' | jq '.'
```

**Calculator Agent:**
```bash
# Get agent card
curl -s http://localhost:3006/calculator/.well-known/agent.json | jq '.'

# Calculate
curl -X POST http://localhost:3006/calculator/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "calculate",
    "parameters": {
      "operation": "multiply",
      "a": 7,
      "b": 8
    }
  }' | jq '.'
```

---

## 7. Observability & Monitoring

### View Metrics

```bash
curl -s http://localhost:15020/metrics | grep -E "list_calls|http_requests"
```

### Check Jaeger Traces

Open in browser: http://localhost:16686

Or query via API:
```bash
curl -s "http://localhost:16686/api/traces?service=agentgateway&limit=10" | jq '.'
```

### View Recent Logs

```bash
docker-compose logs --tail=50 agentgateway
```

### Watch Logs in Real-time

```bash
docker-compose logs -f agentgateway
```

---

## Quick Test All Providers

Run this script to test all providers at once:

```bash
#!/bin/bash

echo "🧪 Testing AgentGateway Providers..."
echo ""

echo "1️⃣ Testing Anthropic..."
curl -s -X POST http://localhost:3000/anthropic/v1/messages \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-haiku-4-5-20251001","max_tokens":50,"messages":[{"role":"user","content":"Hi"}]}' \
  | jq -r '.content[0].text' && echo "✅ Anthropic OK" || echo "❌ Anthropic Failed"
echo ""

echo "2️⃣ Testing OpenAI..."
curl -s -X POST http://localhost:3000/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hi"}],"max_tokens":50}' \
  | jq -r '.choices[0].message.content' && echo "✅ OpenAI OK" || echo "❌ OpenAI Failed"
echo ""

echo "3️⃣ Testing Grok (xAI)..."
curl -s -X POST http://localhost:3000/xai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"grok-4-1-fast-reasoning","messages":[{"role":"user","content":"Hi"}],"max_tokens":50}' \
  | jq -r '.choices[0].message.content' && echo "✅ Grok OK" || echo "❌ Grok Failed"
echo ""

echo "4️⃣ Testing Gemini (Google AI)..."
curl -s -X POST http://localhost:3000/gemini/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-3-pro-preview","messages":[{"role":"user","content":"Hi"}],"max_tokens":50}' \
  | jq -r '.choices[0].message.content' && echo "✅ Gemini OK" || echo "❌ Gemini Failed"
echo ""

echo "5️⃣ Testing MCP Server..."
curl -s -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \
  | jq -r '.result.tools[0].name' && echo "✅ MCP OK" || echo "❌ MCP Failed"
echo ""

echo "6️⃣ Testing Hello Agent..."
curl -s -X POST http://localhost:3000/agent/hello/task \
  -H "Content-Type: application/json" \
  -d '{"skill":"greet","parameters":{"name":"Test","language":"english"}}' \
  | jq -r '.output.text' && echo "✅ Hello Agent OK" || echo "❌ Hello Agent Failed"
echo ""

echo "7️⃣ Testing Calculator Agent..."
curl -s -X POST http://localhost:3000/agent/calculator/task \
  -H "Content-Type: application/json" \
  -d '{"skill":"calculate","parameters":{"operation":"add","a":2,"b":2}}' \
  | jq -r '.output.text' && echo "✅ Calculator Agent OK" || echo "❌ Calculator Agent Failed"
echo ""

echo "✅ All tests complete!"
```

Save this as `test-all.sh`, make it executable (`chmod +x test-all.sh`), and run it!

---

## Troubleshooting

### Check Container Status
```bash
docker-compose ps
```

### Check Logs for Errors
```bash
docker-compose logs agentgateway | grep -i error
```

### Verify API Keys
```bash
# Check if keys are loaded (they should NOT be printed)
docker-compose exec agentgateway env | grep -E "OPENAI|ANTHROPIC|XAI"
```

### Test Gateway Health
```bash
curl http://localhost:3000/health 2>&1 | head -5
```

### Restart All Services
```bash
docker-compose restart
```

---

## Rate Limiting

All AI backends are configured with rate limiting:
- **Limit:** 10 requests per minute
- **Refill:** 10 tokens every 60 seconds

To test rate limiting, run the same request 15+ times rapidly and observe the 429 status codes.

---

## Additional Resources

- **UI Dashboard:** http://localhost:15000/ui/
- **Metrics:** http://localhost:15020/metrics
- **Jaeger Tracing:** http://localhost:16686
- **AgentGateway Docs:** https://agentgateway.dev/docs/

---

## Quick Reference

### Unified Gateway (Port 3000)

| Provider | Endpoint | Default Model |
|----------|----------|---------------|
| Anthropic | `http://localhost:3000/anthropic/v1/...` | claude-haiku-4-5-20251001 |
| OpenAI | `http://localhost:3000/openai/v1/...` | gpt-4o-mini |
| Grok (xAI) | `http://localhost:3000/xai/v1/...` | grok-4-1-fast-reasoning |
| Gemini | `http://localhost:3000/gemini/v1/...` | gemini-3-pro-preview |
| MCP | `http://localhost:3000/mcp` | - |
| A2A Agents | `http://localhost:3000/agent/{name}/...` | - |

### Dedicated Listeners

| Provider | Port | Endpoint | Listener Name |
|----------|------|----------|---------------|
| Anthropic | 3001 | `http://localhost:3001/v1/...` | anthropic-listener |
| OpenAI | 3002 | `http://localhost:3002/v1/...` | openai-listener |
| Grok (xAI) | 3003 | `http://localhost:3003/v1/...` | xai-listener |
| Gemini | 3004 | `http://localhost:3004/v1/...` | gemini-listener |
| MCP | 3005 | `http://localhost:3005/` | mcp-listener |
| A2A Agents | 3006 | `http://localhost:3006/{name}/...` | a2a-listener |
