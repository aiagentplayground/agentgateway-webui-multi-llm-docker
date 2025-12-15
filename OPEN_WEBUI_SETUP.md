# Open WebUI Configuration Guide

This guide explains how to configure Open WebUI to connect to all your AgentGateway LLM providers.

## Quick Start

1. **Start the stack**:
```bash
docker-compose up -d open-webui
```

2. **Access Open WebUI**:
   - URL: http://localhost:8888
   - Create an account on first visit
   - Login with your credentials

## Architecture

Open WebUI connects to each AgentGateway listener as a separate OpenAI-compatible endpoint:

| Provider | Port | Model | AgentGateway Endpoint |
|----------|------|-------|----------------------|
| **Anthropic Claude** | 3001 | claude-haiku-4-5-20251001 | http://agentgateway:3001 |
| **OpenAI GPT** | 3002 | gpt-4o-mini | http://agentgateway:3002 |
| **xAI Grok** | 3003 | grok-4-1-fast-reasoning | http://agentgateway:3003 |
| **Google Gemini** | 3004 | gemini-1.5-flash | http://agentgateway:3004 |

## Adding Connections in Open WebUI

### Step 1: Access Admin Panel

1. Click your profile icon (top right)
2. Select **Settings**
3. Navigate to **Connections** or **Admin Panel** → **Connections**

### Step 2: Add Anthropic Claude Connection

1. Click **"+ Add Connection"** or **"New Connection"**
2. Configure as follows:

```
Connection Name: Anthropic Claude (via AgentGateway)
API Type: OpenAI
Base URL: http://agentgateway:3001/v1
API Key: dummy-key
```

**Available Models:**
- `claude-haiku-4-5-20251001` (default model)
- You can also use the Anthropic native API paths

**Notes:**
- The API key is "dummy-key" because AgentGateway handles authentication
- AgentGateway translates OpenAI format to Anthropic format automatically
- Use `/v1/chat/completions` endpoint (OpenAI compatible)

### Step 3: Add OpenAI GPT Connection

1. Click **"+ Add Connection"**
2. Configure as follows:

```
Connection Name: OpenAI GPT (via AgentGateway)
API Type: OpenAI
Base URL: http://agentgateway:3002/v1
API Key: dummy-key
```

**Available Models:**
- `gpt-4o-mini` (default model)
- Other OpenAI models as configured in AgentGateway

### Step 4: Add xAI Grok Connection

1. Click **"+ Add Connection"**
2. Configure as follows:

```
Connection Name: xAI Grok (via AgentGateway)
API Type: OpenAI
Base URL: http://agentgateway:3003/v1
API Key: dummy-key
```

**Available Models:**
- `grok-4-1-fast-reasoning` (default model)

**Notes:**
- xAI uses OpenAI-compatible API format
- AgentGateway proxies to xAI API

### Step 5: Add Google Gemini Connection

1. Click **"+ Add Connection"**
2. Configure as follows:

```
Connection Name: Google Gemini (via AgentGateway)
API Type: OpenAI
Base URL: http://agentgateway:3004/v1
API Key: dummy-key
```

**Available Models:**
- `gemini-1.5-flash` (default model)

**Notes:**
- AgentGateway translates OpenAI format to Gemini format
- Supports chat completions via unified API

## Model Selection in Chat

Once connections are added:

1. Start a new chat
2. Click the **model selector** dropdown (top of chat)
3. You'll see all configured models grouped by connection:
   - Anthropic Claude (via AgentGateway)
     - claude-haiku-4-5-20251001
   - OpenAI GPT (via AgentGateway)
     - gpt-4o-mini
   - xAI Grok (via AgentGateway)
     - grok-4-1-fast-reasoning
   - Google Gemini (via AgentGateway)
     - gemini-1.5-flash

4. Select any model and start chatting!

## Advanced Configuration

### Using the Unified Gateway (Port 3000)

Instead of individual listeners, you can use the unified gateway:

```
Connection Name: All Providers (Unified)
API Type: OpenAI
Base URL: http://agentgateway:3000
API Key: dummy-key
```

Then specify the provider in the path:
- Anthropic: `http://agentgateway:3000/anthropic/v1`
- OpenAI: `http://agentgateway:3000/openai/v1`
- xAI: `http://agentgateway:3000/xai/v1`
- Gemini: `http://agentgateway:3000/gemini/v1`

### Fetching Available Models

Open WebUI can auto-discover models. Click **"Fetch Models"** or **"Refresh"** after adding a connection.

The models endpoint for each provider:
- Anthropic: `http://agentgateway:3001/v1/models`
- OpenAI: `http://agentgateway:3002/v1/models`
- xAI: `http://agentgateway:3003/v1/models`
- Gemini: `http://agentgateway:3004/v1/models`

### Adding Custom Model IDs

If you want to add other models:

1. Update `agentgateway.yaml` to include new models
2. Restart AgentGateway: `docker-compose restart agentgateway`
3. Refresh models in Open WebUI

Example to add Claude Opus:

```yaml
- ai:
    name: anthropic-opus
    provider:
      anthropic:
        model: claude-opus-4-5-20250929
    routes:
      /v1/messages: messages
      /v1/chat/completions: completions
```

## Testing Connections

### Manual Test with curl

Test each connection from within the Open WebUI container:

```bash
# Test Anthropic
docker-compose exec open-webui curl -X POST http://agentgateway:3001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Test OpenAI
docker-compose exec open-webui curl -X POST http://agentgateway:3002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Test xAI
docker-compose exec open-webui curl -X POST http://agentgateway:3003/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4-1-fast-reasoning",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Test Gemini
docker-compose exec open-webui curl -X POST http://agentgateway:3004/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-1.5-flash",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### From Host Machine

```bash
# Test Anthropic (from host)
curl -X POST http://localhost:3001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "messages": [{"role": "user", "content": "Hello!"}]
  }' | jq

# Test OpenAI (from host)
curl -X POST http://localhost:3002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello!"}]
  }' | jq
```

## Model Capabilities

### Anthropic Claude Haiku
- **Speed**: Fast responses, low latency
- **Context**: 200K tokens
- **Cost**: $3/M input, $15/M output
- **Best for**: Quick tasks, high-volume workloads

### OpenAI GPT-4o-mini
- **Speed**: Very fast
- **Context**: 128K tokens
- **Cost**: $0.15/M input, $0.60/M output
- **Best for**: Cost-effective tasks, high throughput

### xAI Grok
- **Speed**: Fast with reasoning capabilities
- **Context**: Variable
- **Cost**: $2/M input, $10/M output
- **Best for**: Reasoning-heavy tasks

### Google Gemini 1.5 Flash
- **Speed**: Very fast
- **Context**: 1M tokens
- **Cost**: $0.075/M input, $0.30/M output
- **Best for**: Long context, cost-effective

## Monitoring Usage

All requests through Open WebUI will be tracked in:

1. **Grafana Dashboards** (http://localhost:3100)
   - Global Cost Dashboard shows usage across all providers
   - Individual provider dashboards for detailed metrics

2. **Prometheus** (http://localhost:9090)
   - Raw metrics available for custom queries

3. **Jaeger** (http://localhost:16686)
   - Distributed tracing for debugging

## Troubleshooting

### Connection Failed

1. Verify AgentGateway is running:
```bash
docker-compose ps agentgateway
```

2. Check AgentGateway logs:
```bash
docker-compose logs agentgateway
```

3. Verify network connectivity from Open WebUI:
```bash
docker-compose exec open-webui ping agentgateway
```

### Models Not Showing

1. Click **"Fetch Models"** in the connection settings
2. Check AgentGateway `/v1/models` endpoint:
```bash
curl http://localhost:3001/v1/models
curl http://localhost:3002/v1/models
```

3. Ensure `routes` in `agentgateway.yaml` includes `/v1/models: models` or `passthrough`

### Rate Limiting

If you hit rate limits:

1. Check `agentgateway.yaml` rate limit settings:
```yaml
localRateLimit:
  - maxTokens: 10
    tokensPerFill: 10
    fillInterval: 60s
```

2. Increase limits or adjust fill intervals
3. Restart AgentGateway

### API Key Issues

If you see authentication errors:

1. Verify your API keys are set in `.env`:
```bash
cat .env | grep API_KEY
```

2. Restart AgentGateway to pick up new keys:
```bash
docker-compose restart agentgateway
```

## Features

### Chat History
- Automatically saved in Open WebUI
- Persistent across restarts (stored in Docker volume)

### Model Switching
- Switch models mid-conversation
- Compare responses from different providers

### System Prompts
- Set custom system prompts per chat
- Save and reuse prompt templates

### Document Upload
- Upload documents for analysis (if supported by model)
- Works with Claude and GPT models

## Next Steps

1. **Explore Features**: Try different models and compare responses
2. **Set Up Monitoring**: Check Grafana dashboards to track costs
3. **Customize Models**: Add more models to AgentGateway config
4. **Share Access**: Create accounts for team members

## Reference

- Open WebUI Docs: https://docs.openwebui.com/
- AgentGateway Docs: [Link to docs]
- OpenAI API Compatibility: https://platform.openai.com/docs/api-reference

## Configuration Summary

```yaml
# Quick Reference for Open WebUI Connections

Anthropic Claude:
  Base URL: http://agentgateway:3001/v1
  Model: claude-haiku-4-5-20251001
  API Key: dummy-key

OpenAI GPT:
  Base URL: http://agentgateway:3002/v1
  Model: gpt-4o-mini
  API Key: dummy-key

xAI Grok:
  Base URL: http://agentgateway:3003/v1
  Model: grok-4-1-fast-reasoning
  API Key: dummy-key

Google Gemini:
  Base URL: http://agentgateway:3004/v1
  Model: gemini-1.5-flash
  API Key: dummy-key
```
