#!/bin/bash

# Open WebUI Initialization Script
# Automatically configures AgentGateway connections with model IDs

set -e

OPEN_WEBUI_URL="${OPEN_WEBUI_URL:-http://localhost:8888}"
MAX_RETRIES=30
RETRY_DELAY=5

echo "🚀 Open WebUI Initialization Script"
echo "===================================="
echo ""

# Wait for Open WebUI to be ready
echo "⏳ Waiting for Open WebUI to be ready..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -s -f "${OPEN_WEBUI_URL}/health" > /dev/null 2>&1; then
        echo "✅ Open WebUI is ready!"
        break
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        echo "❌ Open WebUI failed to start after ${MAX_RETRIES} attempts"
        exit 1
    fi
    echo "   Attempt $i/$MAX_RETRIES - waiting ${RETRY_DELAY}s..."
    sleep $RETRY_DELAY
done

echo ""
echo "📝 Configuring AgentGateway connections..."
echo ""

# Configuration data
declare -A CONNECTIONS=(
    ["anthropic"]="http://agentgateway:3000/anthropic/v1|claude-haiku-4-5-20251001|Claude Haiku 4.5"
    ["openai"]="http://agentgateway:3000/openai/v1|gpt-5.2-2025-12-11|GPT-5.2"
    ["xai"]="http://agentgateway:3000/xai/v1|grok-4-latest|Grok 4 Latest"
    ["gemini"]="http://agentgateway:3000/gemini/v1|gemini-3-pro-preview|Gemini 3 Pro Preview"
)

# Note: Open WebUI stores connections in its database
# This script provides the configuration that should be manually added
# or can be used to configure via Open WebUI's admin API if available

echo "📋 Configuration Summary:"
echo "========================"
echo ""

for provider in "${!CONNECTIONS[@]}"; do
    IFS='|' read -r url model_id model_name <<< "${CONNECTIONS[$provider]}"
    echo "Provider: ${provider}"
    echo "  URL: ${url}"
    echo "  Model ID: ${model_id}"
    echo "  Model Name: ${model_name}"
    echo ""
done

echo "ℹ️  Manual Configuration Required:"
echo "=================================="
echo ""
echo "Open WebUI does not provide an automated API for configuring"
echo "custom OpenAI-compatible connections via CLI."
echo ""
echo "Please configure manually at: ${OPEN_WEBUI_URL}/admin/settings/connections"
echo ""
echo "For each connection, add the Model ID shown above using the"
echo "'+ Add a model ID' button in the Edit Connection dialog."
echo ""
echo "✨ Once configured, the settings will persist in Open WebUI's database."
echo ""
