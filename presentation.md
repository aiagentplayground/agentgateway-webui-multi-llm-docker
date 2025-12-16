---
title: AgentGateway Multi-LLM Platform
author: Sebastian Maniak
---


# AgentGateway Multi-LLM Platform

## A Unified AI Gateway with SSO & Monitoring

```
    ┌─────────────────┐
    │   Open WebUI    │ ← Web Interface
    │   + Keycloak    │ ← SSO Auth
    └────────┬────────┘
             │
             ↓
    ┌─────────────────┐
    │  AgentGateway   │ ← Unified Gateway
    │  Rate Limiting  │
    └────────┬────────┘
             │
        ┌────┴────┬────────┬────────┐
        ↓         ↓        ↓        ↓
    Anthropic  OpenAI    xAI    Gemini
```

**Press `n` for next slide**

<!-- end_slide -->


# What This Platform Provides

## Core Features

- ✅ **Unified API Gateway** - Single endpoint for 4 AI providers
- ✅ **SSO Authentication** - Keycloak with team management
- ✅ **Web Interface** - Open WebUI with chat interface
- ✅ **Observability** - Prometheus, Grafana, Jaeger tracing
- ✅ **Rate Limiting** - Token bucket policies per provider
- ✅ **Agent System** - MCP tools & A2A agents

<!-- end_slide -->



# Architecture Overview

## Services

| Service | Port | Purpose |
|---------|------|---------|
| Open WebUI | 8888 | Chat interface |
| Keycloak | 8090 | SSO authentication |
| AgentGateway | 3000 | Unified API endpoint |
| Grafana | 3100 | Metrics dashboard |
| Prometheus | 9090 | Metrics collection |
| Jaeger | 16686 | Distributed tracing |

<!-- end_slide -->



# Project Structure

```
agentgateway-webui-multi-llm-docker/
├── agents/              # A2A agent implementations
├── init/
│   ├── keycloak/       # SSO auto-configuration
│   └── openwebui/      # WebUI auto-configuration
├── scripts/            # Utility scripts
├── monitoring/         # Prometheus & Grafana configs
├── docs/               # Documentation
├── agentgateway.yaml   # Main gateway config
└── docker-compose.yml  # Service orchestration
```

<!-- end_slide -->



# Quick Start

## 1. Set Up Environment

```bash
# Copy and edit environment file
cp .env.example .env

# Add your API keys
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
XAI_API_KEY=your-key-here
GEMINI_API_KEY=your-key-here
```

<!-- end_slide -->



# Quick Start (continued)

## 2. Start All Services

```bash
# Build and start everything
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f
```

✅ **Initialization scripts run automatically**

<!-- end_slide -->



# Default Users & Access

## Admin Account
- Email: `admin@example.com`
- Password: `Admin123!`

## Team Accounts

**Marketing:** sarah.johnson, mike.chen (Password: `Marketing123!`)
**Platform:** alex.rivera, jordan.kim (Password: `Platform123!`)
**Security:** taylor.morgan (Password: `Security123!`)

<!-- end_slide -->



# Available AI Models

## 4 Models Through AgentGateway

1. **Claude Haiku 4.5** (claude-haiku-4-5-20251001)
   - Endpoint: `http://localhost:3000/anthropic/v1`

2. **GPT-5.2** (gpt-5.2-2025-12-11)
   - Endpoint: `http://localhost:3000/openai/v1`

3. **Grok 4 Latest** (grok-4-latest)
   - Endpoint: `http://localhost:3000/xai/v1`

4. **Gemini 3 Pro Preview** (gemini-3-pro-preview)
   - Endpoint: `http://localhost:3000/gemini/v1`

<!-- end_slide -->



# Manual Model Configuration

## Step 1: Access Admin Panel

1. Navigate to `http://localhost:8888`
2. Log in as admin:
   - Email: `admin@example.com`
   - Password: `Admin123!`
3. Click **Admin Panel** (top right)
4. Go to **Settings** → **Connections**

<!-- end_slide -->



# Manual Model Configuration

## Step 2: Add Connection #1 (Anthropic)

Click **"+ Add Connection"** and configure:

```
Connection Type: External
URL: http://agentgateway:3000/anthropic/v1
Auth: Bearer
API Key: sk-anthropic
Provider Type: OpenAI
Active: ✓ (toggle ON)
```

**Add Model ID:**
```
claude-haiku-4-5-20251001
```

Click **"Save"**

<!-- end_slide -->



# Manual Model Configuration

## Step 3: Add Connection #2 (OpenAI)

Click **"+ Add Connection"** and configure:

```
Connection Type: External
URL: http://agentgateway:3000/openai/v1
Auth: Bearer
API Key: sk-openai
Provider Type: OpenAI
Active: ✓
```

**Add Model ID:**
```
gpt-5.2-2025-12-11
```

Click **"Save"**

<!-- end_slide -->



# Manual Model Configuration

## Step 4: Add Connection #3 (xAI)

Click **"+ Add Connection"** and configure:

```
Connection Type: External
URL: http://agentgateway:3000/xai/v1
Auth: Bearer
API Key: sk-xai
Provider Type: OpenAI
Active: ✓
```

**Add Model ID:**
```
grok-4-latest
```

Click **"Save"**

<!-- end_slide -->



# Manual Model Configuration

## Step 5: Add Connection #4 (Gemini)

Click **"+ Add Connection"** and configure:

```
Connection Type: External
URL: http://agentgateway:3000/gemini/v1
Auth: Bearer
API Key: sk-gemini
Provider Type: OpenAI
Active: ✓
```

**Add Model ID:**
```
gemini-3-pro-preview
```

Click **"Save"**

<!-- end_slide -->



# Manual Model Configuration

## Step 6: Verify Models

1. Return to the main chat interface
2. Click the **model selector dropdown** (top of chat)
3. You should see all 4 models:
   - Claude Haiku 4.5
   - GPT-5.2
   - Grok 4 Latest
   - Gemini 3 Pro Preview

✅ **Ready to chat!**

<!-- end_slide -->



# Automated Configuration

## Use the Utility Script

Instead of manual configuration, run:

```bash
# Configure all connections automatically
python3 scripts/configure-openwebui-connections.py

# Restart Open WebUI
docker-compose restart open-webui
```

⏱️ **Takes ~30 seconds**

<!-- end_slide -->



# Key Configuration Files

## agentgateway.yaml
- Routes and backends for each AI provider
- Rate limiting policies
- MCP and A2A agent configuration
- Tracing setup

## docker-compose.yml
- All service definitions
- Port mappings
- Environment variables
- Dependencies

<!-- end_slide -->



# Rate Limiting Example

## Token Bucket Policy in agentgateway.yaml

```yaml
policies:
  - name: anthropic-rate-limit
    tokenBucket:
      capacity: 100000      # 100k tokens
      fillRate: 10000       # 10k per period
      period: 1m            # 1 minute
```

**Protects against:**
- Cost overruns
- API quota exhaustion
- Runaway requests

<!-- end_slide -->



# Monitoring & Observability

## Access Points

**Prometheus Metrics:**
```bash
curl http://localhost:15020/metrics
```

**Grafana Dashboards:**
- URL: `http://localhost:3100`
- Login: admin/admin

**Jaeger Tracing:**
- URL: `http://localhost:16686`
- View full request traces

<!-- end_slide -->



# SSO with Keycloak

## Team Management

**3 Pre-configured Teams:**
- Marketing (2 users)
- Platform (2 users)
- Security (1 user)

**Manage Users:**
1. Access: `http://localhost:8090`
2. Login: admin/admin
3. Navigate: agentgateway realm → Users
4. Add/edit users and group memberships

<!-- end_slide -->



# Making API Calls

## Direct Gateway Access

```bash
# Anthropic Claude
curl -X POST http://localhost:3000/anthropic/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

<!-- end_slide -->



# Making API Calls (continued)

## Via OpenAI SDK Format

```bash
# Works with any provider through gateway
curl -X POST http://localhost:3000/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5.2-2025-12-11",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

<!-- end_slide -->



# Troubleshooting

## Models Not Appearing

```bash
# Reconfigure connections
python3 scripts/configure-openwebui-connections.py
docker-compose restart open-webui

# Check logs
docker-compose logs open-webui
```

<!-- end_slide -->



# Troubleshooting (continued)

## SSO Issues

```bash
# Check Keycloak health
docker-compose ps keycloak

# Restart services
docker-compose restart keycloak open-webui

# View initialization logs
docker-compose logs keycloak-init
```

<!-- end_slide -->



# Troubleshooting (continued)

## Gateway Errors

```bash
# Check for errors
docker-compose logs agentgateway | grep -i error

# Verify configuration
docker-compose exec agentgateway cat /etc/agentgateway/agentgateway.yaml

# Test health endpoint
curl http://localhost:3000/health
```

<!-- end_slide -->



# Development Workflow

## Rebuild After Changes

```bash
# Rebuild specific service
docker-compose build agentgateway

# Rebuild everything
docker-compose build

# Rebuild and restart
docker-compose up -d --build
```

<!-- end_slide -->



# Development Workflow (continued)

## Reset Everything

```bash
# Stop all services and remove volumes
docker-compose down -v

# Start fresh
docker-compose up -d

# Reconfigure models
python3 scripts/configure-openwebui-connections.py
```

<!-- end_slide -->



# Utility Scripts

## Available Scripts

**scripts/configure-openwebui-connections.py**
- Automatically configures all 4 API connections
- Updates Open WebUI database
- No manual UI interaction needed

**scripts/configure-models-db.py**
- Legacy script for model configuration
- Alternative approach via database

<!-- end_slide -->



# Adding New AI Providers

## Edit agentgateway.yaml

1. Add new route under port 3000
2. Define backend configuration
3. Add rate limiting policy
4. Update docker-compose.yml for new port (optional)
5. Restart gateway: `docker-compose restart agentgateway`
6. Add connection in Open WebUI

<!-- end_slide -->



# MCP Integration

## Model Context Protocol

**Access MCP tools at:**
```
http://localhost:3000/mcp/sse
```

**Example tools configured:**
- Everything server (filesystem, git, etc.)
- Custom tool integrations

**Edit:** `agentgateway.yaml` backends section

<!-- end_slide -->



# A2A Agents

## Agent-to-Agent Communication

**Pre-configured agents:**
- Hello Agent (port 9001)
- Calculator Agent (port 9002)

**Access via:**
```bash
curl http://localhost:3000/agent/hello
curl http://localhost:3000/agent/calculator
```

**Add agents:** Edit `agents/` directory

<!-- end_slide -->



# Security Considerations

## ⚠️ This is a Development Setup

**For Production:**
1. ✅ Change all default passwords
2. ✅ Enable SSL/TLS (use HTTPS)
3. ✅ Use secrets management (not .env)
4. ✅ Configure Keycloak production mode
5. ✅ Set up proper network policies
6. ✅ Enable authentication on metrics
7. ✅ Review CORS settings
8. ✅ Implement proper secret rotation

<!-- end_slide -->



# Port Reference Summary

| Service | Port | Access |
|---------|------|--------|
| Open WebUI | 8888 | `http://localhost:8888` |
| Keycloak | 8090 | `http://localhost:8090` |
| Gateway (Main) | 3000 | `http://localhost:3000` |
| Gateway (Admin) | 15000 | `http://localhost:15000/ui` |
| Grafana | 3100 | `http://localhost:3100` |
| Prometheus | 9090 | `http://localhost:9090` |
| Jaeger | 16686 | `http://localhost:16686` |

<!-- end_slide -->



# Key Takeaways

## What You Get

✅ **One Command Deploy** - `docker-compose up -d`
✅ **Automatic Setup** - Users, models, SSO configured
✅ **Production-Ready** - Rate limiting, tracing, metrics
✅ **Multi-Provider** - 4 AI models, unified interface
✅ **Team Management** - SSO with role-based access
✅ **Fully Documented** - README + presentation + guides

<!-- end_slide -->



# Next Steps

## Getting Started

1. ✅ Set up `.env` with API keys
2. ✅ Run `docker-compose up -d`
3. ✅ Access `http://localhost:8888`
4. ✅ Log in and start chatting
5. ✅ Explore monitoring dashboards
6. ✅ Customize `agentgateway.yaml`

**📚 Documentation:** See `README.md` and `docs/`

<!-- end_slide -->



# Questions?

## Resources

- **README.md** - Complete setup guide
- **docs/** - Detailed documentation
- **agentgateway.yaml** - Gateway configuration
- **scripts/** - Automation utilities

## Support

```bash
# Check logs
docker-compose logs <service>

# View configuration
docker-compose config

# Service status
docker-compose ps
```

<!-- end_slide -->



# Thank You!

## AgentGateway Multi-LLM Platform

```
       🚀 Ready to Deploy
       🔒 Secure by Default
       📊 Observable & Traceable
       🤖 Multi-Provider AI Access
```

**Start chatting with AI models today!**

`http://localhost:8888`

<!-- end_slide -->
