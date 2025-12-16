#!/usr/bin/env python3
"""
Configure Open WebUI Connections
=================================

This script automatically configures API connections in Open WebUI
by updating the database configuration.
"""

import subprocess
import json

CONTAINER_NAME = "open-webui"

# Connections to configure
CONNECTIONS = [
    {
        "name": "Anthropic (Claude)",
        "url": "http://agentgateway:3000/anthropic/v1",
        "api_key": "sk-anthropic",
        "models": ["claude-haiku-4-5-20251001"]
    },
    {
        "name": "OpenAI (GPT)",
        "url": "http://agentgateway:3000/openai/v1",
        "api_key": "sk-openai",
        "models": ["gpt-5.2-2025-12-11"]
    },
    {
        "name": "xAI (Grok)",
        "url": "http://agentgateway:3000/xai/v1",
        "api_key": "sk-xai",
        "models": ["grok-4-latest"]
    },
    {
        "name": "Gemini",
        "url": "http://agentgateway:3000/gemini/v1",
        "api_key": "sk-gemini",
        "models": ["gemini-3-pro-preview"]
    }
]

def main():
    print("="*70)
    print("Configuring Open WebUI Connections")
    print("="*70)
    print()

    # Build the configuration
    openai_api_base_urls = [conn["url"] for conn in CONNECTIONS]
    openai_api_keys = [conn["api_key"] for conn in CONNECTIONS]

    script = f"""
import sqlite3
import json

conn = sqlite3.connect('/app/backend/data/webui.db')
cursor = conn.cursor()

# Get or create config
cursor.execute('SELECT id, data FROM config')
result = cursor.fetchone()

if result:
    config_id, config_data = result
    data = json.loads(config_data)
else:
    config_id = 1
    data = {{}}

# Update config with connection settings
data['ENABLE_OPENAI_API'] = True
data['OPENAI_API_BASE_URLS'] = {json.dumps(openai_api_base_urls)}
data['OPENAI_API_KEYS'] = {json.dumps(openai_api_keys)}

# Save back to database
if result:
    cursor.execute('UPDATE config SET data = ?, updated_at = datetime("now") WHERE id = ?',
                   (json.dumps(data), config_id))
else:
    cursor.execute('INSERT INTO config (id, data, version, created_at, updated_at) VALUES (?, ?, 0, datetime("now"), datetime("now"))',
                   (config_id, json.dumps(data)))

conn.commit()

print("✓ Connection configuration added to database")
print()
print("Configured URLs:")
for url in data['OPENAI_API_BASE_URLS']:
    print(f"  • {{url}}")

conn.close()
"""

    print("Adding connection configurations to database...")
    print()

    result = subprocess.run(
        ["docker", "exec", CONTAINER_NAME, "python3", "-c", script],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print("Errors:")
        print(result.stderr)
        print()

    print()
    print("="*70)
    print("Next Steps")
    print("="*70)
    print()
    print("1. Restart Open WebUI to apply changes:")
    print("   docker-compose restart open-webui")
    print()
    print("2. Log in as admin at: http://localhost:8888")
    print("   Email: admin@example.com")
    print("   Password: Admin123!")
    print()
    print("3. Go to: Admin Panel → Settings → Connections")
    print()
    print("4. The models should now be available in the model selector")
    print()
    print("Models configured:")
    for conn in CONNECTIONS:
        print(f"  • {conn['name']}")
        for model in conn['models']:
            print(f"    - {model}")
    print()
    print("="*70)
    print()


if __name__ == "__main__":
    main()
