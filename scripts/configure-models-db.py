#!/usr/bin/env python3
"""
Configure Models in Open WebUI Database
========================================

This script adds model configurations directly to the Open WebUI database.
"""

import subprocess
import json

CONTAINER_NAME = "open-webui"

# Configuration to add to the database
CONFIG_UPDATES = {
    # Enable OpenAI API
    "ENABLE_OPENAI_API": True,

    # OpenAI API configurations
    "OPENAI_API_BASE_URLS": [
        "http://agentgateway:3000/anthropic/v1",
        "http://agentgateway:3000/openai/v1",
        "http://agentgateway:3000/xai/v1",
        "http://agentgateway:3000/gemi/v1"
    ],

    "OPENAI_API_KEYS": [
        "sk-anthropic",
        "sk-openai",
        "sk-xai",
        "sk-gemini"
    ]
}

def main():
    print("="*70)
    print("Configuring Models in Open WebUI")
    print("="*70)
    print()

    # Model configurations
    models = [
        {
            "id": "claude-haiku-4-5-20251001",
            "name": "Anthropic (Claude) - claude-haiku-4-5-20251001",
            "base_url": "http://agentgateway:3000/anthropic/v1",
            "api_key": "sk-anthropic"
        },
        {
            "id": "gpt-5.2-2025-12-11",
            "name": "OpenAI (GPT) - gpt-5.2-2025-12-11",
            "base_url": "http://agentgateway:3000/openai/v1",
            "api_key": "sk-openai"
        },
        {
            "id": "grok-4-latest",
            "name": "xAI (Grok) - grok-4-latest",
            "base_url": "http://agentgateway:3000/xai/v1",
            "api_key": "sk-xai"
        },
        {
            "id": "gemini-3-pro-preview",
            "name": "Gemini - gemini-3-pro-preview",
            "base_url": "http://agentgateway:3000/gemini/v1",
            "api_key": "sk-gemini"
        }
    ]

    script = f"""
import sqlite3
import json
import time

conn = sqlite3.connect('/app/backend/data/webui.db')
cursor = conn.cursor()

# Check if config table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
if not cursor.fetchone():
    print("Config table does not exist")
    conn.close()
    exit(1)

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
data['OPENAI_API_BASE_URLS'] = [
    "http://agentgateway:3000/anthropic/v1",
    "http://agentgateway:3000/openai/v1",
    "http://agentgateway:3000/xai/v1",
    "http://agentgateway:3000/gemini/v1"
]
data['OPENAI_API_KEYS'] = [
    "sk-anthropic",
    "sk-openai",
    "sk-xai",
    "sk-gemini"
]

# Configure openai section if it doesn't exist
if 'openai' not in data:
    data['openai'] = {{}}

data['openai']['enable'] = True
data['openai']['api_base_urls'] = data['OPENAI_API_BASE_URLS']
data['openai']['api_keys'] = data['OPENAI_API_KEYS']

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

# Add models to the model table
models_data = {json.dumps(models)}
timestamp = int(time.time())

print("\\nAdding models to database...")
models_added = 0

for model_data in models_data:
    model_id = model_data['id']
    model_name = model_data['name']
    base_url = model_data['base_url']
    api_key = model_data['api_key']

    # Check if model already exists
    cursor.execute('SELECT id FROM model WHERE id = ?', (model_id,))
    if cursor.fetchone():
        print(f"  • Model {{model_id}} already exists, skipping")
        continue

    # Create model entry
    meta = json.dumps({{
        "profile_image_url": "/static/favicon.png",
        "description": f"{{model_name}} via AgentGateway",
        "capabilities": {{}},
        "position": models_added
    }})

    params = json.dumps({{
        "api_base_url": base_url,
        "api_key": api_key,
        "stream": True
    }})

    # Insert model - empty user_id makes it system-wide
    cursor.execute(
        'INSERT INTO model (id, user_id, base_model_id, name, meta, params, created_at, updated_at, is_active, access_control) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (model_id, '', model_id, model_name, meta, params, timestamp, timestamp, 1, json.dumps({{"read": {{"group_ids": [], "user_ids": []}}, "write": {{"group_ids": [], "user_ids": []}}}}))
    )

    models_added += 1
    print(f"  • Added model: {{model_name}}")

conn.commit()
print(f"\\n✓ Added {{models_added}} new models to database")

conn.close()
"""

    print("Adding model configurations to database...")
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
    print("2. Sign in at: http://localhost:8888")
    print()
    print("3. The models should now appear in the model selector")
    print()
    print("If models still don't appear, check Admin Panel → Settings")
    print("and verify the OpenAI API settings are enabled.")
    print()
    print("="*70)
    print()


if __name__ == "__main__":
    main()
