# AgentGateway Web UI

A beautiful, interactive web interface for testing all AgentGateway providers, MCP tools, and A2A agents.

## Features

### 🤖 LLM Provider Testing
Test all four LLM providers with an easy-to-use chat interface:
- **Anthropic Claude** (Haiku 4.5)
- **OpenAI** (GPT-4o-mini)
- **xAI** (Grok 4.1 Fast Reasoning)
- **Google Gemini** (1.5 Flash)

### 🔧 MCP Tools
Interact with Model Context Protocol tools:
- List available tools
- Execute echo tool
- JSON-RPC interface made simple

### 👥 A2A Agents
Test Agent-to-Agent communication:
- **Hello Agent**: Multi-language greetings
- **Calculator Agent**: Math operations (add, subtract, multiply, divide, power, sqrt)

## Access

Open your browser and navigate to:

```
http://localhost:8080
```

## Architecture

- **Frontend**: Pure HTML/CSS/JavaScript (no build process)
- **Server**: Nginx Alpine (lightweight)
- **API**: Connects to AgentGateway at `localhost:3000`

## Files

- `index.html` - Main UI with responsive design
- `app.js` - JavaScript application logic
- `Dockerfile` - Nginx container configuration

## Development

To modify the UI:

1. Edit `index.html` or `app.js`
2. Rebuild the container:
   ```bash
   docker-compose up -d --build webui
   ```
3. Refresh your browser

## Design

The UI features:
- Modern gradient background
- Clean card-based layout
- Tab-based navigation
- Real-time response display
- Loading indicators
- Error handling with visual feedback
- Fully responsive design

Perfect for demos, presentations, and hands-on testing!
