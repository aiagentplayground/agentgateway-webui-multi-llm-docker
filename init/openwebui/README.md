# Open WebUI Auto-Initialization

This Docker container automatically initializes Open WebUI with users and model configurations.

## What It Does

1. **Waits for Open WebUI** to be ready
2. **Creates Admin User** with configured credentials
3. **Creates Team Users**:
   - Marketing Team (2 users)
   - Platform Team (2 users)
   - Security Team (1 user)
4. **Configures AI Models** (via environment variables)

## Configuration

Edit `config.json` to customize:

- Admin credentials
- User accounts and teams
- Model endpoints

## Usage

### Automatic (Recommended)

The init container runs automatically when you start the stack:

```bash
docker-compose up -d
```

The `openwebui-init` service will:
- Run once on startup
- Create all users
- Exit when complete

### Manual Run

To re-run initialization:

```bash
# Rebuild if you changed config.json
docker-compose build openwebui-init

# Run the initialization
docker-compose up openwebui-init
```

### Check Logs

```bash
docker-compose logs openwebui-init
```

## Default Credentials

### Admin
- Email: `admin@example.com`
- Password: `Admin123!`

### Marketing Team
- Sarah Johnson: `sarah.marketing@example.com` / `Marketing123!`
- Mike Chen: `mike.marketing@example.com` / `Marketing123!`

### Platform Team
- Alex Rivera: `alex.platform@example.com` / `Platform123!`
- Jordan Kim: `jordan.platform@example.com` / `Platform123!`

### Security Team
- Taylor Morgan: `taylor.security@example.com` / `Security123!`

**⚠️ IMPORTANT:** Change all passwords after first login!

## Models Configured

The following AI models are pre-configured:

1. **Anthropic Claude Haiku 4.5**
   - Endpoint: `http://agentgateway:3000/anthropic/v1`

2. **OpenAI GPT-5.2**
   - Endpoint: `http://agentgateway:3000/openai/v1`

3. **xAI Grok 4 Latest**
   - Endpoint: `http://agentgateway:3000/xai/v1`

4. **Google Gemini 3 Pro Preview**
   - Endpoint: `http://agentgateway:3000/gemini/v1`

All models are routed through AgentGateway with rate limiting and monitoring.

## Troubleshooting

### Users Not Created

If signup is disabled after admin creation:

1. Stop all containers:
   ```bash
   docker-compose down
   ```

2. Remove Open WebUI data (⚠️ this deletes all Open WebUI data):
   ```bash
   docker volume rm agentgateway-webui-multi-llm-docker_open-webui-data
   ```

3. Start fresh:
   ```bash
   docker-compose up -d
   ```

### Init Container Exits Too Fast

Check if Open WebUI is healthy:

```bash
docker-compose ps open-webui
docker-compose logs open-webui
```

### Models Not Showing

Models are configured via environment variables in `docker-compose.yml`.
Check the `OPENAI_API_BASE_URLS` and `MODELS` environment variables.

## Customization

### Adding More Users

Edit `config.json` and add to the `users` array:

```json
{
  "email": "newuser@example.com",
  "password": "Password123!",
  "name": "New User",
  "team": "engineering",
  "role": "user"
}
```

### Changing Admin Password

Edit `config.json`:

```json
{
  "admin": {
    "email": "admin@example.com",
    "password": "YourSecurePassword123!",
    "name": "Admin User"
  }
}
```

Then rebuild and rerun:

```bash
docker-compose build openwebui-init
docker-compose up openwebui-init
```

## Security Notes

1. **Change Default Passwords**: All default passwords should be changed immediately
2. **API Keys**: Actual AI provider API keys are set in the `.env` file
3. **Network Isolation**: Init container only runs on the internal Docker network
4. **One-Time Execution**: Init container exits after completion (no persistent access)

## Integration with AgentGateway

All AI requests from Open WebUI flow through AgentGateway, providing:

- **Unified API**: Single endpoint for all AI providers
- **Rate Limiting**: 10 requests per minute per service (configurable)
- **Monitoring**: Full tracing via Jaeger
- **Metrics**: Prometheus metrics and Grafana dashboards
- **Cost Control**: Prevent excessive API usage

## Files

- `Dockerfile` - Container definition
- `config.json` - User and model configuration
- `init-openwebui.py` - Initialization script
- `README.md` - This file
