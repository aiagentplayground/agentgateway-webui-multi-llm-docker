#!/usr/bin/env python3
"""
Open WebUI Model Configuration Script
Automatically adds model IDs to AgentGateway connections in Open WebUI
"""

import json
import os
import sys
import time
import requests
from urllib.parse import urljoin

OPEN_WEBUI_URL = os.environ.get("OPEN_WEBUI_URL", "http://localhost:8888")
MAX_RETRIES = 30
RETRY_DELAY = 5

# Model configurations for each AgentGateway provider
MODELS_CONFIG = {
    "anthropic": {
        "url": "http://agentgateway:3000/anthropic/v1",
        "model_id": "claude-haiku-4-5-20251001",
        "name": "Claude Haiku 4.5"
    },
    "openai": {
        "url": "http://agentgateway:3000/openai/v1",
        "model_id": "gpt-5.2-2025-12-11",
        "name": "GPT-5.2"
    },
    "xai": {
        "url": "http://agentgateway:3000/xai/v1",
        "model_id": "grok-4-latest",
        "name": "Grok 4 Latest"
    },
    "gemini": {
        "url": "http://agentgateway:3000/gemini/v1",
        "model_id": "gemini-3-pro-preview",
        "name": "Gemini 3 Pro Preview"
    }
}

def wait_for_openwebui():
    """Wait for Open WebUI to be ready"""
    print("⏳ Waiting for Open WebUI to be ready...")

    for i in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(f"{OPEN_WEBUI_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Open WebUI is ready!")
                return True
        except requests.exceptions.RequestException:
            pass

        if i == MAX_RETRIES:
            print(f"❌ Open WebUI failed to start after {MAX_RETRIES} attempts")
            return False

        print(f"   Attempt {i}/{MAX_RETRIES} - waiting {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)

    return False

def print_configuration():
    """Print the configuration summary"""
    print("\n📋 Model Configuration:")
    print("=" * 60)

    for provider, config in MODELS_CONFIG.items():
        print(f"\n{provider.upper()}:")
        print(f"  Base URL: {config['url']}")
        print(f"  Model ID: {config['model_id']}")
        print(f"  Model Name: {config['name']}")

    print("\n" + "=" * 60)

def main():
    print("🚀 Open WebUI Model Configuration Script")
    print("=" * 60)

    if not wait_for_openwebui():
        sys.exit(1)

    print_configuration()

    print("\nℹ️  Configuration Method:")
    print("-" * 60)
    print("\nOpen WebUI connections are managed through the web interface.")
    print("The model IDs above need to be added manually:")
    print(f"\n1. Go to: {OPEN_WEBUI_URL}/admin/settings/connections")
    print("2. For each connection, click 'Edit'")
    print("3. In 'Model IDs' section, click '+ Add a model ID'")
    print("4. Enter the Model ID from the configuration above")
    print("5. Click 'Save'")
    print("\n✨ Once configured, settings persist in Open WebUI's database.")
    print("\n💡 Tip: Copy the Model IDs from the output above!")
    print("\nModel IDs to add:")
    for provider, config in MODELS_CONFIG.items():
        print(f"  • {provider}: {config['model_id']}")

    print("\n✅ Script complete! Please configure models manually in the UI.")

if __name__ == "__main__":
    main()
