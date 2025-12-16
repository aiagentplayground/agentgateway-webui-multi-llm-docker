# How to Add AI Models in Open WebUI

The models need to be added through the Open WebUI admin interface. Follow these steps:

## Step-by-Step Instructions

### 1. Access Open WebUI Admin Panel

1. Go to: **http://localhost:8888**
2. Sign in with admin credentials:
   - **Email:** `admin@example.com`
   - **Password:** `Admin123!`
3. Click the **Settings icon (⚙️)** in the bottom left
4. Navigate to **Admin Panel**

### 2. Add OpenAI API Connections

1. In the Admin Panel, look for **Connections** or **Settings** → **Connections**
2. You should see a section for **OpenAI API**
3. Click **Add Connection** or the **+** button

### 3. Add Each AI Model Connection

Add the following 4 connections:

#### Connection 1: Anthropic Claude
```
API Base URL: http://agentgateway:3000/anthropic/v1
API Key: sk-anthropic
```

#### Connection 2: OpenAI GPT
```
API Base URL: http://agentgateway:3000/openai/v1
API Key: sk-openai
```

#### Connection 3: xAI Grok
```
API Base URL: http://agentgateway:3000/xai/v1
API Key: sk-xai
```

#### Connection 4: Google Gemini
```
API Base URL: http://agentgateway:3000/gemini/v1
API Key: sk-gemini
```

### 4. Verify Models Are Available

1. Go back to the main chat interface
2. Click the **model selector** dropdown (usually at the top)
3. You should see all 4 models:
   - Claude Haiku 4.5
   - GPT-5.2
   - Grok 4 Latest
   - Gemini 3 Pro Preview

### 5. Test a Model

1. Select one of the models
2. Send a test message: "Hello, can you tell me what model you are?"
3. Verify you get a response

## Alternative: Using Admin Settings

If you don't see "Connections", try:

1. Go to **Settings** → **Admin Settings**
2. Look for **External Connections** or **Models**
3. Enable **OpenAI API**
4. Add the URLs and keys as shown above

## Troubleshooting

### Models Not Appearing

**Check AgentGateway is running:**
```bash
docker-compose ps agentgateway
```

**Check AgentGateway logs:**
```bash
docker-compose logs agentgateway | tail -50
```

**Test AgentGateway endpoints:**
```bash
# Test Anthropic
curl http://localhost:3000/anthropic/v1/models

# Test OpenAI
curl http://localhost:3000/openai/v1/models

# Test xAI
curl http://localhost:3000/xai/v1/chat/completions

# Test Gemini
curl http://localhost:3000/gemini/v1/models
```

### Connection Errors

If you see connection errors:

1. Make sure you're using `http://agentgateway:3000` (internal Docker network)
2. NOT `http://localhost:3000` (won't work from inside container)
3. The format is: `http://agentgateway:3000/{provider}/v1`

### Models Show But Don't Respond

Check that AgentGateway has the real API keys:

1. Edit your `.env` file (create if it doesn't exist):
   ```bash
   ANTHROPIC_API_KEY=your_actual_anthropic_key
   OPENAI_API_KEY=your_actual_openai_key
   XAI_API_KEY=your_actual_xai_key
   GEMINI_API_KEY=your_actual_gemini_key
   ```

2. Restart services:
   ```bash
   docker-compose restart agentgateway open-webui
   ```

## Quick Reference

| Model | Endpoint |
|-------|----------|
| Claude Haiku 4.5 | `http://agentgateway:3000/anthropic/v1` |
| GPT-5.2 | `http://agentgateway:3000/openai/v1` |
| Grok 4 Latest | `http://agentgateway:3000/xai/v1` |
| Gemini 3 Pro | `http://agentgateway:3000/gemini/v1` |

**API Keys for all:** Use the placeholder keys (`sk-anthropic`, `sk-openai`, etc.) in Open WebUI. AgentGateway will use the real keys from the environment.

## Need Help?

If models still don't appear:

1. Check Open WebUI version: `docker exec open-webui env | grep VERSION`
2. Look at Open WebUI logs: `docker-compose logs open-webui | tail -100`
3. Restart Open WebUI: `docker-compose restart open-webui`

The UI layout may vary slightly depending on your Open WebUI version, but the concept is the same: add OpenAI-compatible API connections with the AgentGateway endpoints.
