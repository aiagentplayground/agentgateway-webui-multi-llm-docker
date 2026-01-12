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

    # Build models data
    models_data = []
    for i, conn_config in enumerate(CONNECTIONS):
        for model in conn_config["models"]:
            models_data.append({
                "id": model,
                "name": f"{conn_config['name']} - {model}",
                "base_url": conn_config["url"],
                "api_key_index": i
            })

    script = f"""
import sqlite3
import json
import time

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

# Configure openai section if it doesn't exist
if 'openai' not in data:
    data['openai'] = {{}}

data['openai']['enable'] = True
data['openai']['api_base_urls'] = {json.dumps(openai_api_base_urls)}
data['openai']['api_keys'] = {json.dumps(openai_api_keys)}

# THIS IS THE CRITICAL PART - Configure api_configs with model_ids
data['openai']['api_configs'] = {{
    '0': {{
        'enable': True,
        'tags': [],
        'prefix_id': '',
        'model_ids': ['claude-haiku-4-5-20251001'],
        'connection_type': 'external',
        'auth_type': 'bearer'
    }},
    '1': {{
        'enable': True,
        'tags': [],
        'prefix_id': '',
        'model_ids': ['gpt-5.2-2025-12-11'],
        'connection_type': 'external',
        'auth_type': 'bearer'
    }},
    '2': {{
        'enable': True,
        'tags': [],
        'prefix_id': '',
        'model_ids': ['grok-4-latest'],
        'connection_type': 'external',
        'auth_type': 'bearer'
    }},
    '3': {{
        'enable': True,
        'tags': [],
        'prefix_id': '',
        'model_ids': ['gemini-3-pro-preview'],
        'connection_type': 'external',
        'auth_type': 'bearer'
    }}
}}

# Disable automatic model fetching to avoid errors
data['ENABLE_MODEL_FILTER'] = False

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
print()

# Add models to the model table
models_data = {json.dumps(models_data)}
timestamp = int(time.time())

print("Adding models to database...")
models_added = 0

for model_data in models_data:
    model_id = model_data['id']
    model_name = model_data['name']
    base_url = model_data['base_url']
    api_key_idx = model_data['api_key_index']

    # Check if model already exists
    cursor.execute('SELECT id FROM model WHERE id = ?', (model_id,))
    if cursor.fetchone():
        print(f"  • Model {{model_id}} already exists, skipping")
        continue

    # Create model entry with proper meta and params
    meta = json.dumps({{
        "profile_image_url": "/static/favicon.png",
        "description": f"{{model_name}} via AgentGateway",
        "capabilities": {{}},
        "position": models_added
    }})

    params = json.dumps({{
        "api_base_url": base_url,
        "api_key": data['OPENAI_API_KEYS'][api_key_idx],
        "stream": True
    }})

    # Insert model - use empty string for user_id to make it system-wide
    cursor.execute('''
        INSERT INTO model (id, user_id, base_model_id, name, meta, params, created_at, updated_at, is_active, access_control)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (model_id, '', model_id, model_name, meta, params, timestamp, timestamp, 1, json.dumps({{"read": {{"group_ids": [], "user_ids": []}}, "write": {{"group_ids": [], "user_ids": []}}}})))

    models_added += 1
    print(f"  • Added model: {{model_name}}")

conn.commit()
print()
print(f"✓ Added {{models_added}} new models to database")

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
