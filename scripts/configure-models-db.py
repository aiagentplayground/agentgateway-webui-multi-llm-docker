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

    script = """
import sqlite3
import json

conn = sqlite3.connect('/app/backend/data/webui.db')
cursor = conn.cursor()

# Check if config table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
if not cursor.fetchone():
    print("Config table does not exist")
    conn.close()
    exit(1)

# Get current config
cursor.execute("SELECT * FROM config")
configs = cursor.fetchall()

print("Current configurations:")
for config in configs:
    print(f"  {config}")

# Update or insert OPENAI_API_BASE_URLS
cursor.execute("""
    INSERT OR REPLACE INTO config (key, value, created_at, updated_at)
    VALUES (?, ?, datetime('now'), datetime('now'))
""", ('OPENAI_API_BASE_URLS', 'http://agentgateway:3000/anthropic/v1;http://agentgateway:3000/openai/v1;http://agentgateway:3000/xai/v1;http://agentgateway:3000/gemini/v1'))

# Update or insert OPENAI_API_KEYS
cursor.execute("""
    INSERT OR REPLACE INTO config (key, value, created_at, updated_at)
    VALUES (?, ?, datetime('now'), datetime('now'))
""", ('OPENAI_API_KEYS', 'sk-anthropic;sk-openai;sk-xai;sk-gemini'))

# Enable OpenAI API
cursor.execute("""
    INSERT OR REPLACE INTO config (key, value, created_at, updated_at)
    VALUES (?, ?, datetime('now'), datetime('now'))
""", ('ENABLE_OPENAI_API', 'true'))

conn.commit()

print("\\n✓ Model configurations added to database")

# Show updated config
cursor.execute("SELECT key, value FROM config WHERE key LIKE '%OPENAI%' OR key LIKE '%MODEL%'")
configs = cursor.fetchall()

print("\\nUpdated configurations:")
for config in configs:
    print(f"  {config[0]}: {config[1]}")

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
