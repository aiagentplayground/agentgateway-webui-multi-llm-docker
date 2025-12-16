# AgentGateway Multi-LLM Platform

A complete multi-provider AI platform with unified gateway, SSO authentication, and comprehensive monitoring.

## Overview

This platform provides:
- **Unified AI Gateway**: Single endpoint for multiple AI providers (Anthropic, OpenAI, xAI, Gemini)
- **SSO Authentication**: Keycloak-based single sign-on with team management
- **Web Interface**: Open WebUI with pre-configured models and connections
- **Monitoring**: Prometheus, Grafana, and Jaeger for observability
- **Agent System**: MCP and A2A agent integration

📊 **[View Platform Presentation](presentation.md)** - Interactive slides covering architecture, setup, and manual model configuration. Run with: `presenterm presentation.md`


## Architecture

```
┌─────────────────┐
│   Open WebUI    │ ← User Interface (Port 8888)
│   + Keycloak    │ ← SSO Authentication (Port 8090)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  AgentGateway   │ ← Unified Gateway (Port 3000)
│  Rate Limiting  │ ← Individual ports: 3001-3006
│  Tracing        │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ↓         ↓        ↓        ↓
Anthropic  OpenAI    xAI    Gemini
```

## Project Structure

```
.
├── agents/                      # A2A Agent implementations
│   ├── hello-agent.js
│   ├── calculator-agent.js
│   └── Dockerfile
│
├── init/                        # Initialization scripts
│   ├── keycloak/               # Keycloak SSO setup
│   │   ├── init-keycloak.py   # Auto-configure realms & users
│   │   ├── realm-config.json  # Realm configuration
│   │   └── Dockerfile
│   └── openwebui/              # Open WebUI setup
│       ├── init-openwebui.py  # Auto-configure users & models
│       ├── config.json        # Configuration
│       └── Dockerfile
│
├── scripts/                     # Utility scripts
│   ├── configure-openwebui-connections.py  # Setup API connections
│   └── configure-models-db.py              # Configure models
│
├── webui/                       # Open WebUI frontend
│   └── Dockerfile
│
├── monitoring/                  # Monitoring configuration
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       ├── provisioning/
│       └── dashboards/
│
├── agentgateway.yaml           # Main gateway configuration
├── docker-compose.yml          # Service orchestration
└── .env                        # Environment variables (API keys)
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- API keys for AI providers (set in `.env`)

### 1. Set Up Environment

```bash
cp .env.example .env
# Edit .env and add your API keys:
# ANTHROPIC_API_KEY=your-key
# OPENAI_API_KEY=your-key
# XAI_API_KEY=your-key
# GEMINI_API_KEY=your-key
```

### 2. Start Services

```bash
docker-compose up -d
```

This will start all services and run initialization scripts automatically.

### 3. Access Services

- **Open WebUI**: http://localhost:8888
- **Keycloak Admin**: http://localhost:8090 (admin/admin)
- **AgentGateway Admin**: http://localhost:15000/ui
- **Grafana**: http://localhost:3100 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686

## Default Users

### Admin Account
- **Email**: admin@example.com
- **Password**: Admin123!
- **Role**: Administrator

### Team Accounts

**Marketing Team**
- sarah.johnson / Marketing123!
- mike.chen / Marketing123!

**Platform Team**
- alex.rivera / Platform123!
- jordan.kim / Platform123!

**Security Team**
- taylor.morgan / Security123!

## Available Models

The platform provides access to 4 AI models through AgentGateway:

1. **Claude Haiku 4.5** (claude-haiku-4-5-20251001)
   - Endpoint: http://localhost:3000/anthropic/v1

2. **GPT-5.2** (gpt-5.2-2025-12-11)
   - Endpoint: http://localhost:3000/openai/v1

3. **Grok 4 Latest** (grok-4-latest)
   - Endpoint: http://localhost:3000/xai/v1

4. **Gemini 3 Pro Preview** (gemini-3-pro-preview)
   - Endpoint: http://localhost:3000/gemini/v1

## Configuration

### Adding Models

Models are automatically configured during initialization. To reconfigure:

```bash
python3 scripts/configure-openwebui-connections.py
docker-compose restart open-webui
```

### Modifying Gateway Routes

Edit `agentgateway.yaml` to:
- Add new AI providers
- Configure rate limits
- Set up custom policies
- Add MCP tools or A2A agents

After changes:
```bash
docker-compose restart agentgateway
```

### Managing Users

Users are managed through Keycloak:
1. Access Keycloak Admin Console: http://localhost:8090
2. Navigate to: agentgateway realm → Users
3. Add/edit users and assign to groups (marketing, platform, security)

## Monitoring

### Metrics
- **Prometheus**: Scrapes metrics from AgentGateway (port 15020)
- **Grafana**: Visualizes metrics with pre-configured dashboards

### User & Team Analytics
- **Track Usage by User**: Monitor which users and teams are using which LLM providers
- **Cost Attribution**: View request counts and token usage per user
- **Grafana Dashboard**: Pre-built **User & Team Analytics** dashboard
- **Per-User Metrics**: Response times, request rates, and provider preferences
- 📊 See [User Tracking Documentation](docs/USER_TRACKING.md) for details

### Tracing
- **Jaeger**: Distributed tracing for all AI requests
- View traces at http://localhost:16686

## Utility Scripts

### Configure Open WebUI Connections
```bash
python3 scripts/configure-openwebui-connections.py
```
Automatically configures all AI provider connections in Open WebUI.

### Configure Models Database
```bash
python3 scripts/configure-models-db.py
```
Adds model configurations to the Open WebUI database.

## Development

### Rebuild Services

```bash
# Rebuild specific service
docker-compose build <service-name>

# Rebuild all
docker-compose build

# Rebuild and restart
docker-compose up -d --build
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f agentgateway
docker-compose logs -f open-webui
docker-compose logs -f keycloak
```

### Reset Everything

```bash
docker-compose down -v
docker-compose up -d
```

## Troubleshooting

### Models Not Appearing

1. Check connections are configured:
   ```bash
   python3 scripts/configure-openwebui-connections.py
   docker-compose restart open-webui
   ```

2. Log in as admin and verify in: Admin Panel → Settings → Connections

### SSO Login Issues

1. Verify Keycloak is healthy:
   ```bash
   docker-compose ps keycloak
   ```

2. Check Open WebUI OIDC configuration in docker-compose.yml

3. Restart services:
   ```bash
   docker-compose restart keycloak open-webui
   ```

### AgentGateway Errors

1. Check configuration syntax:
   ```bash
   docker-compose logs agentgateway | grep -i error
   ```

2. Verify API keys in `.env` file

3. Check health endpoint:
   ```bash
   curl http://localhost:3000/health
   ```

## API Usage Examples

### Direct API Calls

```bash
# Anthropic
curl -X POST http://localhost:3000/anthropic/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -d '{"model": "claude-haiku-4-5-20251001", "messages": [{"role": "user", "content": "Hello!"}], "max_tokens": 100}'

# OpenAI
curl -X POST http://localhost:3000/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{"model": "gpt-5.2-2025-12-11", "messages": [{"role": "user", "content": "Hello!"}]}'
```

### Via Open WebUI

1. Log in at http://localhost:8888
2. Select a model from the dropdown
3. Start chatting!

## Port Reference

| Service | Port | Description |
|---------|------|-------------|
| AgentGateway (Unified) | 3000 | Main gateway endpoint |
| AgentGateway (Anthropic) | 3001 | Anthropic-only |
| AgentGateway (OpenAI) | 3002 | OpenAI-only |
| AgentGateway (xAI) | 3003 | xAI-only |
| AgentGateway (Gemini) | 3004 | Gemini-only |
| AgentGateway (MCP) | 3005 | MCP tools |
| AgentGateway (A2A) | 3006 | Agent-to-Agent |
| AgentGateway (Admin) | 15000 | Admin UI |
| AgentGateway (Metrics) | 15020 | Prometheus metrics |
| Open WebUI | 8888 | Web interface |
| Keycloak | 8090 | SSO authentication |
| Grafana | 3100 | Metrics dashboard |
| Prometheus | 9090 | Metrics collection |
| Jaeger | 16686 | Trace viewing |

## Security Notes

**⚠️ This is a development setup. For production:**

1. Change all default passwords
2. Use proper SSL/TLS certificates
3. Configure Keycloak for production mode
4. Set up proper network security
5. Use secrets management for API keys
6. Enable proper authentication on all endpoints
7. Configure CORS properly
8. Review and harden all security settings

## License

[Your License]

## Support

For issues and questions:
- Check logs: `docker-compose logs <service>`
- Review configuration in `agentgateway.yaml` and `docker-compose.yml`
- Consult service documentation
