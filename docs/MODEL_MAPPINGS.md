# Model Mappings & Connection Reference

Quick reference for all available models and their connections through AgentGateway.

## Connection Endpoints

### From Open WebUI (Docker Network)

| Connection Name | Base URL | Port | Model ID |
|----------------|----------|------|----------|
| **Anthropic Claude** | `http://agentgateway:3001/v1` | 3001 | `claude-haiku-4-5-20251001` |
| **OpenAI GPT** | `http://agentgateway:3002/v1` | 3002 | `gpt-4o-mini` |
| **xAI Grok** | `http://agentgateway:3003/v1` | 3003 | `grok-4-1-fast-reasoning` |
| **Google Gemini** | `http://agentgateway:3004/v1` | 3004 | `gemini-1.5-flash` |

### From Host Machine (Testing)

| Provider | Base URL | Model ID |
|----------|----------|----------|
| **Anthropic Claude** | `http://localhost:3001/v1` | `claude-haiku-4-5-20251001` |
| **OpenAI GPT** | `http://localhost:3002/v1` | `gpt-4o-mini` |
| **xAI Grok** | `http://localhost:3003/v1` | `grok-4-1-fast-reasoning` |
| **Google Gemini** | `http://localhost:3004/v1` | `gemini-1.5-flash` |

## Model Details

### 1. Anthropic Claude Haiku (Port 3001)

**Model ID**: `claude-haiku-4-5-20251001`

**Specifications**:
- Context Window: 200,000 tokens
- Max Output: 8,192 tokens
- Pricing:
  - Input: $3.00 per 1M tokens
  - Output: $15.00 per 1M tokens

**API Routes**:
- `/v1/chat/completions` - OpenAI-compatible format
- `/v1/messages` - Native Anthropic format
- `/v1/models` - List available models

**Best For**:
- Fast reasoning and analysis
- High-volume workloads
- Cost-effective long conversations
- Tool/function calling

**Example Request**:
```bash
curl -X POST http://localhost:3001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain quantum computing"}
    ],
    "max_tokens": 1024
  }'
```

---

### 2. OpenAI GPT-4o-mini (Port 3002)

**Model ID**: `gpt-4o-mini`

**Specifications**:
- Context Window: 128,000 tokens
- Max Output: 16,384 tokens
- Pricing:
  - Input: $0.15 per 1M tokens
  - Output: $0.60 per 1M tokens

**API Routes**:
- `/v1/chat/completions` - Chat completions
- `/v1/models` - List available models

**Best For**:
- Most cost-effective option
- High-throughput applications
- Simple to moderate complexity tasks
- JSON mode and structured outputs

**Example Request**:
```bash
curl -X POST http://localhost:3002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "What is AI?"}
    ],
    "temperature": 0.7
  }'
```

---

### 3. xAI Grok (Port 3003)

**Model ID**: `grok-4-1-fast-reasoning`

**Specifications**:
- Context Window: Variable (check xAI docs)
- Max Output: Variable
- Pricing:
  - Input: $2.00 per 1M tokens
  - Output: $10.00 per 1M tokens

**API Routes**:
- `/v1/chat/completions` - OpenAI-compatible format
- `/v1/models` - List available models

**Best For**:
- Complex reasoning tasks
- Multi-step problem solving
- Real-time information (if enabled)
- Fast inference

**Example Request**:
```bash
curl -X POST http://localhost:3003/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4-1-fast-reasoning",
    "messages": [
      {"role": "user", "content": "Solve this logic puzzle: ..."}
    ]
  }'
```

---

### 4. Google Gemini 1.5 Flash (Port 3004)

**Model ID**: `gemini-1.5-flash`

**Specifications**:
- Context Window: 1,000,000 tokens
- Max Output: 8,192 tokens
- Pricing:
  - Input: $0.075 per 1M tokens
  - Output: $0.30 per 1M tokens

**API Routes**:
- `/v1/chat/completions` - OpenAI-compatible format
- `/v1/models` - List available models

**Best For**:
- Extremely long context tasks
- Document analysis
- Most cost-effective for large inputs
- Multimodal capabilities (images, video)

**Example Request**:
```bash
curl -X POST http://localhost:3004/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-1.5-flash",
    "messages": [
      {"role": "user", "content": "Analyze this document: ..."}
    ]
  }'
```

---

## Rate Limiting

All endpoints have rate limiting configured in `agentgateway.yaml`:

```yaml
localRateLimit:
  - maxTokens: 10
    tokensPerFill: 10
    fillInterval: 60s
```

This allows:
- **10 requests** burst capacity
- **10 requests per minute** sustained

To change limits, edit `agentgateway.yaml` and restart AgentGateway.

## Cost Comparison (Per Million Tokens)

| Provider | Input Cost | Output Cost | Total (50/50 split) |
|----------|------------|-------------|---------------------|
| **Gemini 1.5 Flash** | $0.075 | $0.30 | **$0.1875** ⭐ Most economical |
| **OpenAI GPT-4o-mini** | $0.15 | $0.60 | **$0.375** |
| **xAI Grok** | $2.00 | $10.00 | **$6.00** |
| **Anthropic Claude Haiku** | $3.00 | $15.00 | **$9.00** |

> **Note**: Costs assume 50% input / 50% output token split. Actual costs vary based on usage patterns.

## Context Window Comparison

| Provider | Context Window | Best For |
|----------|---------------|----------|
| **Gemini 1.5 Flash** | 1M tokens | Long documents, entire codebases |
| **Anthropic Claude Haiku** | 200K tokens | Books, large conversations |
| **OpenAI GPT-4o-mini** | 128K tokens | Standard applications |
| **xAI Grok** | Variable | Check xAI documentation |

## Choosing the Right Model

### For Cost Optimization
1. **Gemini 1.5 Flash** - Best cost per token
2. **GPT-4o-mini** - Good balance of cost and quality
3. **Grok** - Mid-range pricing with reasoning
4. **Claude Haiku** - Premium but fast and accurate

### For Long Context
1. **Gemini 1.5 Flash** - 1M tokens
2. **Claude Haiku** - 200K tokens
3. **GPT-4o-mini** - 128K tokens

### For Speed
1. **GPT-4o-mini** - Very fast
2. **Gemini 1.5 Flash** - Fast
3. **Claude Haiku** - Fast
4. **Grok** - Fast with reasoning

### For Reasoning Tasks
1. **Grok** - Designed for reasoning
2. **Claude Haiku** - Strong reasoning
3. **GPT-4o-mini** - Good reasoning
4. **Gemini** - Capable reasoning

## Adding More Models

To add additional models, edit `agentgateway.yaml`:

### Example: Adding Claude Opus

```yaml
- port: 3007
  listeners:
  - name: anthropic-opus-listener
    routes:
    - name: anthropic-opus
      policies:
        localRateLimit:
          - maxTokens: 10
            tokensPerFill: 10
            fillInterval: 60s
        backendAuth:
          key: "$ANTHROPIC_API_KEY"
      backends:
      - ai:
          name: anthropic-opus
          provider:
            anthropic:
              model: claude-opus-4-5-20250929
          routes:
            /v1/messages: messages
            /v1/chat/completions: completions
            /v1/models: passthrough
```

Then add to docker-compose.yml:
```yaml
ports:
  - "3007:3007"   # Anthropic Opus listener
```

## Monitoring

Track usage across all models in Grafana:

1. **Global Cost Dashboard**: http://localhost:3100/d/global-llm-cost
   - Shows cost breakdown by provider
   - Token usage comparison
   - Request rates

2. **Individual Dashboards**:
   - Anthropic: http://localhost:3100/d/anthropic-metrics
   - OpenAI: http://localhost:3100/d/openai-metrics
   - xAI: http://localhost:3100/d/xai-metrics
   - Gemini: http://localhost:3100/d/gemini-metrics

## Testing All Models

Run this script to test all models:

```bash
#!/bin/bash

echo "Testing Anthropic Claude..."
curl -s -X POST http://localhost:3001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-haiku-4-5-20251001","messages":[{"role":"user","content":"Say hi"}]}' | jq -r '.choices[0].message.content'

echo -e "\nTesting OpenAI GPT..."
curl -s -X POST http://localhost:3002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hi"}]}' | jq -r '.choices[0].message.content'

echo -e "\nTesting xAI Grok..."
curl -s -X POST http://localhost:3003/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"grok-4-1-fast-reasoning","messages":[{"role":"user","content":"Say hi"}]}' | jq -r '.choices[0].message.content'

echo -e "\nTesting Google Gemini..."
curl -s -X POST http://localhost:3004/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-1.5-flash","messages":[{"role":"user","content":"Say hi"}]}' | jq -r '.choices[0].message.content'
```

Save as `test-models.sh` and run:
```bash
chmod +x test-models.sh
./test-models.sh
```
