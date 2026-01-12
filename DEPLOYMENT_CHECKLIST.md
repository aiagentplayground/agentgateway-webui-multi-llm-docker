# Deployment Checklist

Use this checklist to deploy the AgentGateway Multi-LLM Platform from scratch.

## ✅ Pre-Deployment

- [ ] Docker Engine 20.10+ installed
- [ ] Docker Compose 2.0+ installed
- [ ] Python 3 installed
- [ ] At least 4GB RAM available
- [ ] At least 10GB disk space available
- [ ] At least one AI provider API key obtained

## ✅ Step 1: Environment Setup

```bash
cd agentgateway-webui-multi-llm-docker
cp .env.example .env
```

- [ ] `.env` file created
- [ ] Added at least one API key to `.env`
- [ ] (Optional) Changed database passwords in `.env`

**Required API keys (at least one):**
- [ ] `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com/
- [ ] `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
- [ ] `XAI_API_KEY` - Get from https://console.x.ai
- [ ] `GEMINI_API_KEY` - Get from https://aistudio.google.com/app/apikey

## ✅ Step 2: Start Services

```bash
docker-compose up -d
```

- [ ] Command executed successfully
- [ ] Wait 60-90 seconds for services to start
- [ ] All containers show "Up" in `docker-compose ps`

## ✅ Step 3: Configure Models (CRITICAL!)

```bash
python3 scripts/configure-models-db.py
docker-compose restart open-webui
sleep 10
```

- [ ] Script ran without errors
- [ ] Open WebUI restarted successfully
- [ ] Waited 10 seconds for startup

## ✅ Step 4: Verify Deployment

### Check Services

- [ ] Open WebUI accessible at http://localhost:8888
- [ ] Can log in with admin@example.com / Admin123!
- [ ] Keycloak accessible at http://localhost:8090
- [ ] AgentGateway admin accessible at http://localhost:15000/ui
- [ ] Grafana accessible at http://localhost:3100

### Check Models

- [ ] Logged into Open WebUI as admin
- [ ] Model selector dropdown shows 4 models:
  - [ ] claude-haiku-4-5-20251001
  - [ ] gpt-5.2-2025-12-11
  - [ ] grok-4-latest
  - [ ] gemini-3-pro-preview

### Test a Model

- [ ] Selected a model from dropdown
- [ ] Sent test message: "Hello! Can you introduce yourself?"
- [ ] Received response from AI model
- [ ] Response time reasonable (< 30 seconds for first message)

### Check Monitoring

- [ ] Prometheus targets UP at http://localhost:9090/targets
- [ ] Grafana showing metrics at http://localhost:3100
- [ ] Jaeger showing traces at http://localhost:16686
- [ ] AgentGateway metrics visible at http://localhost:15020/metrics

## ✅ Step 5: Post-Deployment (Optional)

### Create Additional Users

Via Keycloak:
- [ ] Logged into Keycloak admin console
- [ ] Selected "agentgateway" realm
- [ ] Created users in appropriate groups (marketing, platform, security)

### Customize Configuration

- [ ] Reviewed `agentgateway.yaml` for rate limits
- [ ] Adjusted rate limits if needed
- [ ] Configured additional monitoring if needed

### Security Hardening (Production Only)

- [ ] Changed all default passwords
- [ ] Configured SSL/TLS certificates
- [ ] Set up proper network security
- [ ] Enabled authentication on monitoring endpoints
- [ ] Configured proper CORS settings
- [ ] Reviewed Keycloak security settings

## 🚨 Troubleshooting

If anything fails, check:

1. **Models not appearing:**
   ```bash
   python3 scripts/configure-models-db.py
   docker-compose restart open-webui
   ```

2. **Services not starting:**
   ```bash
   docker-compose logs <service-name>
   ```

3. **API errors:**
   - Verify API keys in `.env`
   - Check `docker-compose logs agentgateway`

4. **Complete reset:**
   ```bash
   docker-compose down -v
   docker-compose up -d
   python3 scripts/configure-models-db.py
   docker-compose restart open-webui
   ```

See [README.md](README.md#troubleshooting) for detailed troubleshooting steps.

## ✅ Deployment Complete!

- [ ] All checks passed
- [ ] Platform is operational
- [ ] Users can access and chat with AI models
- [ ] Monitoring is working

**Next steps:**
1. Create additional user accounts
2. Customize rate limits and policies
3. Set up alerts in Grafana
4. Review security settings for production use

---

**Deployment Date:** ________________

**Deployed By:** ________________

**Notes:**
