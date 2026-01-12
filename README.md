# AgentGateway Multi-LLM Platform

A complete multi-provider AI platform with unified gateway, SSO authentication, and comprehensive monitoring.

## TL;DR - Quick Deploy

```bash
# 1. Set up environment
cp .env.example .env
nano .env  # Add your API keys

# 2. Start everything
docker-compose up -d

# 3. Configure models (REQUIRED!)
python3 scripts/configure-models-db.py
docker-compose restart open-webui

# 4. Access Open WebUI
# http://localhost:8888
# Login: admin@example.com / Admin123!
```

**That's it!** All 4 models should now work.

📋 **[Deployment Checklist](DEPLOYMENT_CHECKLIST.md)** - Print this and check off items as you deploy.

See [full deployment guide](#deployment-guide---from-scratch) below for detailed steps.

## Overview

This platform provides:
- **Unified AI Gateway**: Single endpoint for multiple AI providers (Anthropic, OpenAI, xAI, Gemini)
- **SSO Authentication**: Keycloak-based single sign-on with team management
- **Web Interface**: Open WebUI with pre-configured models and connections
- **Monitoring**: Prometheus, Grafana, and Jaeger for observability
- **Agent System**: MCP and A2A agent integration

📊 **[View Platform Presentation](presentation.md)** - Interactive slides covering architecture, setup, and manual model configuration. Run with: `presenterm presentation.md`

## Quick Reference

**Essential Commands:**
```bash
# Start everything
docker-compose up -d

# Configure models (REQUIRED after first start)
python3 scripts/configure-models-db.py && docker-compose restart open-webui

# Check status
docker-compose ps

# View logs
docker-compose logs -f <service-name>

# Complete reset
docker-compose down -v && docker-compose up -d
```

**Default Access:**
- Open WebUI: http://localhost:8888 (admin@example.com / Admin123!)
- Keycloak: http://localhost:8090 (admin / admin)
- Grafana: http://localhost:3100 (admin / admin)


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

## Deployment Guide - From Scratch

Follow these steps to deploy the complete platform from scratch.

### Prerequisites

Before starting, ensure you have:

1. **Docker Engine** (20.10+) and **Docker Compose** (2.0+)
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Python 3** (for configuration scripts)
   ```bash
   python3 --version
   ```

3. **API Keys** for at least one AI provider:
   - Anthropic Claude: https://console.anthropic.com/
   - OpenAI: https://platform.openai.com/api-keys
   - xAI (Grok): https://x.ai/
   - Google Gemini: https://makersuite.google.com/app/apikey

4. **System Resources**:
   - Minimum: 4GB RAM, 10GB disk space
   - Recommended: 8GB RAM, 20GB disk space

### Step 1: Clone and Configure Environment

```bash
# Clone the repository (or navigate to your project directory)
cd agentgateway-webui-multi-llm-docker

# Create .env file from example
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required .env configuration:**
```bash
# AI Provider API Keys (add at least one)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
XAI_API_KEY=xai-xxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxx

# Database passwords (change in production)
KEYCLOAK_DB_PASSWORD=keycloak_secure_password
POSTGRES_PASSWORD=postgres_secure_password
```

### Step 2: Start All Services

```bash
# Start the entire platform
docker-compose up -d

# This will start:
# - AgentGateway (main API gateway)
# - Open WebUI (chat interface)
# - Keycloak (SSO authentication)
# - PostgreSQL (Keycloak database)
# - Prometheus, Grafana, Jaeger (monitoring)
# - Hello Agent & Calculator Agent (A2A examples)
# - Init containers (auto-configuration)
```

**Wait for services to be ready** (~60-90 seconds):
```bash
# Check service status
docker-compose ps

# All services should show "Up" or "healthy"
# The openwebui-init container will exit after completing setup
```

### Step 3: Configure Models (CRITICAL)

The init container attempts to configure models automatically, but **you must verify and complete the configuration**:

```bash
# Run the model configuration script
python3 scripts/configure-models-db.py

# Restart Open WebUI to apply changes
docker-compose restart open-webui

# Wait 10 seconds for Open WebUI to start
sleep 10
```

**Why this step is critical:** Open WebUI requires specific database configuration that includes:
- API endpoint URLs
- API keys
- Model IDs mapped to each endpoint
- Connection settings

See [MODEL_CONFIGURATION_FIX.md](MODEL_CONFIGURATION_FIX.md) for technical details.

### Step 4: Verify Deployment

#### 4.1 Check Service Health

```bash
# Check all containers are running
docker-compose ps

# Expected output:
# - agentgateway: Up (healthy)
# - open-webui: Up (healthy)
# - keycloak: Up (healthy)
# - postgres-keycloak: Up (healthy)
# - jaeger: Up
# - prometheus: Up
# - grafana: Up
# - hello-agent: Up
# - calculator-agent: Up
# - openwebui-init: Exited (0)  ← This is normal
```

#### 4.2 Access Web Interfaces

Open your browser and verify access to:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Open WebUI** | http://localhost:8888 | admin@example.com / Admin123! |
| **Keycloak Admin** | http://localhost:8090 | admin / admin |
| **AgentGateway Admin** | http://localhost:15000/ui | No auth required |
| **Grafana** | http://localhost:3100 | admin / admin |
| **Prometheus** | http://localhost:9090 | No auth required |
| **Jaeger Tracing** | http://localhost:16686 | No auth required |

#### 4.3 Verify Models in Open WebUI

1. Go to http://localhost:8888
2. Log in with: **admin@example.com** / **Admin123!**
3. Look at the **model selector dropdown** at the top of the chat interface
4. You should see **4 models**:
   - claude-haiku-4-5-20251001
   - gpt-5.2-2025-12-11
   - grok-4-latest
   - gemini-3-pro-preview

**If models are NOT visible**, see [Troubleshooting: Models Not Appearing](#models-not-appearing)

#### 4.4 Test a Model

1. In Open WebUI, select any model from the dropdown
2. Type a test message: "Hello! Can you introduce yourself?"
3. Verify you get a response from the AI model

**Common first-message delays:**
- First request may take 10-30 seconds (cold start)
- Subsequent requests should be faster (2-5 seconds)

#### 4.5 Verify Monitoring

```bash
# Check AgentGateway is exposing metrics
curl -s http://localhost:15020/metrics | head -20

# Check Prometheus is scraping
# Visit: http://localhost:9090/targets
# All targets should be "UP"

# Check Jaeger is receiving traces
# Visit: http://localhost:16686
# Select "agentgateway" service and click "Find Traces"
```

### Step 5: Access Services

All services are now ready:

- **Open WebUI**: http://localhost:8888
  - Primary chat interface for users
  - Login with admin@example.com / Admin123!

- **Keycloak Admin**: http://localhost:8090
  - Manage users, teams, and SSO settings
  - Login with admin / admin

- **AgentGateway Admin**: http://localhost:15000/ui
  - View gateway configuration and routes
  - Monitor real-time traffic

- **Grafana**: http://localhost:3100
  - View metrics dashboards
  - Track usage by user/team
  - Login with admin / admin

- **Prometheus**: http://localhost:9090
  - Query raw metrics
  - View targets and alerts

- **Jaeger**: http://localhost:16686
  - Distributed tracing
  - Debug request flows

### Step 6: Create Additional Users (Optional)

#### Via Keycloak Admin Console:

1. Go to http://localhost:8090
2. Login as admin / admin
3. Select **agentgateway** realm (dropdown at top-left)
4. Navigate to **Users** → **Add User**
5. Fill in user details and assign to groups:
   - **marketing** - Marketing team members
   - **platform** - Platform/engineering team
   - **security** - Security team

#### Via Open WebUI (if signup enabled):

1. Go to http://localhost:8888
2. Click "Sign up"
3. Complete registration form

**Note:** By default, signup is disabled. Admin must create users.

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

### Configuring Models

Models need to be configured after first deployment. Use the configuration script:

```bash
# Recommended script (configures everything correctly)
python3 scripts/configure-models-db.py
docker-compose restart open-webui

# Alternative script (does the same thing)
python3 scripts/configure-openwebui-connections.py
docker-compose restart open-webui
```

**What these scripts do:**
1. Configure API base URLs and keys
2. Set up model IDs for each endpoint (critical!)
3. Add models to the database
4. Disable automatic model fetching (prevents errors)

**Verify models are working:**
1. Go to http://localhost:8888
2. Log in as admin@example.com / Admin123!
3. Check the model selector dropdown
4. All 4 models should be visible:
   - claude-haiku-4-5-20251001
   - gpt-5.2-2025-12-11
   - grok-4-latest
   - gemini-3-pro-preview

See [MODEL_CONFIGURATION_FIX.md](MODEL_CONFIGURATION_FIX.md) for technical details about why this step is necessary.

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

### Configure Models Database (RECOMMENDED)
```bash
python3 scripts/configure-models-db.py
```
**Use this script** to configure all AI models in Open WebUI. It:
- Sets up API base URLs and keys
- Configures model IDs for each endpoint
- Adds models to the database
- Disables automatic model fetching

**When to use:** After first deployment, or anytime models aren't appearing.

### Configure Open WebUI Connections (ALTERNATIVE)
```bash
python3 scripts/configure-openwebui-connections.py
```
Alternative script that does the same thing as `configure-models-db.py`. Use whichever you prefer.

### Track User Activity
```bash
python3 scripts/track-users-openwebui.py
```
Monitor which users are making requests to which AI providers.

### Analyze User Activity
```bash
python3 scripts/analyze-user-activity.py
```
Generate reports on user activity, token usage, and cost attribution.

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

**Symptom:** Model dropdown in Open WebUI is empty or only shows some models.

**Root Cause:** Open WebUI requires models to be configured in THREE places:
1. API base URLs and keys (connection settings)
2. `openai.api_configs` with `model_ids` (CRITICAL - this was often missing!)
3. Entries in the `model` table

**Solution:**

```bash
# Step 1: Run the configuration script
python3 scripts/configure-models-db.py

# Step 2: Restart Open WebUI
docker-compose restart open-webui

# Step 3: Wait for startup
sleep 10

# Step 4: Clear browser cache and refresh
# In your browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

**Verify the fix:**
```bash
# Check database configuration
docker exec open-webui python3 -c "
import sqlite3, json
conn = sqlite3.connect('/app/backend/data/webui.db')
cursor = conn.cursor()
cursor.execute('SELECT data FROM config')
data = json.loads(cursor.fetchone()[0])
print('Models configured:', data.get('openai', {}).get('api_configs', {}).keys())
conn.close()
"
```

**Alternative script:**
```bash
# Use the connections script instead
python3 scripts/configure-openwebui-connections.py
docker-compose restart open-webui
```

**Manual configuration via UI:**
1. Log in to Open WebUI as admin
2. Go to: **Admin Panel** → **Settings** → **Connections**
3. For each API endpoint, click **Edit**
4. Under **Model IDs**, manually add the model ID
5. Click **Save**

**See also:** [MODEL_CONFIGURATION_FIX.md](MODEL_CONFIGURATION_FIX.md) for technical details.

### Models Show Error When Used

**Symptom:** Models appear in dropdown but give errors when you try to chat.

**Possible causes:**

1. **Invalid API Key**
   ```bash
   # Check your .env file has correct keys
   cat .env | grep -E "ANTHROPIC|OPENAI|XAI|GEMINI"

   # Restart AgentGateway to pick up changes
   docker-compose restart agentgateway
   ```

2. **AgentGateway not routing correctly**
   ```bash
   # Check AgentGateway logs
   docker-compose logs agentgateway --tail 50

   # Look for errors related to API calls
   docker-compose logs agentgateway | grep -i error
   ```

3. **Rate limiting**
   ```bash
   # Check if you're hitting rate limits
   docker-compose logs agentgateway | grep -i "rate limit"
   ```

4. **Network connectivity**
   ```bash
   # Test connectivity from Open WebUI to AgentGateway
   docker exec open-webui curl -s http://agentgateway:3000/health

   # Should return: {"status":"ok"} or similar
   ```

### SSO Login Issues

**Symptom:** Can't log in with Keycloak SSO, or OAuth errors.

**Solutions:**

1. **Verify Keycloak is healthy:**
   ```bash
   docker-compose ps keycloak
   # Should show "Up (healthy)"

   docker-compose logs keycloak --tail 50
   ```

2. **Check Keycloak realm configuration:**
   - Access: http://localhost:8090
   - Login: admin / admin
   - Verify **agentgateway** realm exists
   - Check **open-webui** client is configured

3. **Verify Open WebUI OIDC configuration:**
   ```bash
   # Check environment variables
   docker exec open-webui env | grep OAUTH
   ```

4. **Common fixes:**
   ```bash
   # Restart both services
   docker-compose restart keycloak open-webui

   # If still not working, check logs
   docker-compose logs open-webui | grep -i oauth
   docker-compose logs keycloak | grep -i error
   ```

5. **Reset Keycloak (last resort):**
   ```bash
   docker-compose down
   docker volume rm agentgateway-webui-multi-llm-docker_keycloak-postgres-data
   docker-compose up -d
   # Note: This deletes all Keycloak data!
   ```

### AgentGateway Errors

**Symptom:** API requests fail, 500 errors, or gateway not responding.

1. **Check configuration syntax:**
   ```bash
   # View recent errors
   docker-compose logs agentgateway | grep -i error

   # Check if gateway started correctly
   docker-compose logs agentgateway | head -50
   ```

2. **Verify API keys in `.env` file:**
   ```bash
   # Check .env file exists and has keys
   cat .env

   # Restart to pick up changes
   docker-compose restart agentgateway
   ```

3. **Check YAML configuration:**
   ```bash
   # Validate YAML syntax (requires yq or yamllint)
   yamllint agentgateway.yaml

   # Or just check for obvious errors
   cat agentgateway.yaml | grep -E "^[^ ]|error"
   ```

4. **Test health endpoint:**
   ```bash
   # From host
   curl http://localhost:3000/health

   # From inside Open WebUI container
   docker exec open-webui curl http://agentgateway:3000/health
   ```

5. **Check resource usage:**
   ```bash
   docker stats agentgateway --no-stream
   # High CPU/memory might indicate issues
   ```

### Container Won't Start

**Symptom:** Service shows as "Restarting" or "Exited" in `docker-compose ps`.

1. **Check logs for specific error:**
   ```bash
   docker-compose logs <service-name>
   ```

2. **Common issues:**

   **Port conflicts:**
   ```bash
   # Check if ports are already in use
   netstat -tulpn | grep -E "3000|8888|8090"

   # Or on Mac:
   lsof -i :3000
   lsof -i :8888
   ```

   **Volume permissions:**
   ```bash
   # Fix volume ownership
   docker-compose down
   sudo chown -R $USER:$USER .
   docker-compose up -d
   ```

   **Out of memory:**
   ```bash
   # Check Docker resources
   docker system df
   docker system prune  # Clean up unused resources
   ```

3. **Reset specific service:**
   ```bash
   # Remove and recreate container
   docker-compose rm -f <service-name>
   docker-compose up -d <service-name>
   ```

### Database Issues

**Symptom:** Open WebUI can't save settings, or Keycloak can't authenticate.

1. **Check PostgreSQL (Keycloak database):**
   ```bash
   docker-compose logs postgres-keycloak

   # Test connection
   docker exec postgres-keycloak pg_isready
   ```

2. **Check Open WebUI database:**
   ```bash
   # Verify database file exists
   docker exec open-webui ls -lh /app/backend/data/webui.db

   # Check database integrity
   docker exec open-webui sqlite3 /app/backend/data/webui.db "PRAGMA integrity_check;"
   ```

3. **Reset Open WebUI database (WARNING: Deletes all data!):**
   ```bash
   docker-compose down
   docker volume rm agentgateway-webui-multi-llm-docker_open-webui-data
   docker-compose up -d
   ```

### Monitoring Not Working

**Symptom:** Grafana shows no data, Prometheus can't scrape metrics, or Jaeger has no traces.

1. **Check Prometheus targets:**
   - Visit: http://localhost:9090/targets
   - All targets should be **UP**
   - If down, check service connectivity

2. **Verify AgentGateway metrics:**
   ```bash
   curl http://localhost:15020/metrics | head -20
   # Should show Prometheus-formatted metrics
   ```

3. **Check Grafana data source:**
   - Visit: http://localhost:3100
   - Go to: Configuration → Data Sources
   - Test connection to Prometheus

4. **Verify Jaeger is receiving traces:**
   ```bash
   # Make a test request through AgentGateway
   curl -X POST http://localhost:3000/anthropic/v1/messages \
     -H "Content-Type: application/json" \
     -d '{"model": "claude-haiku-4-5-20251001", "messages": [{"role": "user", "content": "test"}], "max_tokens": 10}'

   # Check Jaeger UI for the trace
   # Visit: http://localhost:16686
   ```

### Complete Reset

**If all else fails, reset the entire platform:**

```bash
# Stop all services
docker-compose down

# Remove all volumes (WARNING: Deletes all data!)
docker volume rm agentgateway-webui-multi-llm-docker_open-webui-data
docker volume rm agentgateway-webui-multi-llm-docker_keycloak-postgres-data
docker volume rm agentgateway-webui-multi-llm-docker_prometheus-data
docker volume rm agentgateway-webui-multi-llm-docker_grafana-data

# Rebuild images
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Wait for services to start
sleep 60

# Configure models
python3 scripts/configure-models-db.py
docker-compose restart open-webui
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
