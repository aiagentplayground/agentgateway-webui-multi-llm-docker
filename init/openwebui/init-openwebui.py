#!/usr/bin/env python3
"""
Open WebUI Initialization Script
=================================

This script automatically initializes Open WebUI with:
- Admin user
- Team users (marketing, platform, security)
- AI model configurations

It runs as a Docker container on startup and is idempotent.
"""

import json
import time
import sys
import os
from typing import Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class OpenWebUIInitializer:
    """Handles Open WebUI initialization"""

    def __init__(self, config_path: str = "/app/config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.base_url = self.config['openwebui_url']
        self.session = self.create_session()
        self.admin_token: Optional[str] = None

    def create_session(self) -> requests.Session:
        """Create a session with retry logic"""
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def wait_for_openwebui(self, max_attempts: int = 30) -> bool:
        """Wait for Open WebUI to be ready"""
        print("Waiting for Open WebUI to be ready...")

        for attempt in range(max_attempts):
            try:
                response = self.session.get(
                    f"{self.base_url}/health",
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"✓ Open WebUI is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass

            # Also try the main page
            try:
                response = self.session.get(
                    self.base_url,
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"✓ Open WebUI is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass

            print(f"  Attempt {attempt + 1}/{max_attempts}... waiting")
            time.sleep(5)

        print("✗ Timeout waiting for Open WebUI")
        return False

    def check_if_initialized(self) -> bool:
        """Check if Open WebUI has been initialized"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/auths/",
                timeout=10
            )
            # If we get any response, it means the API is up
            return response.status_code in [200, 401, 403]
        except:
            return False

    def create_admin(self) -> bool:
        """Create admin user"""
        admin = self.config['admin']
        print(f"\nCreating admin user: {admin['email']}")

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auths/signup",
                json={
                    "email": admin['email'],
                    "password": admin['password'],
                    "name": admin['name']
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                print(f"✓ Admin user created successfully")
                return True
            elif response.status_code == 400:
                # Admin might already exist, try to sign in
                print(f"ℹ Admin might already exist, attempting sign in...")
                return self.signin_admin()
            else:
                print(f"✗ Failed to create admin: {response.status_code}")
                print(f"  Response: {response.text}")
                # Try to sign in anyway
                return self.signin_admin()

        except Exception as e:
            print(f"✗ Error creating admin: {e}")
            # Try to sign in anyway
            return self.signin_admin()

    def signin_admin(self) -> bool:
        """Sign in as admin"""
        admin = self.config['admin']
        print(f"Signing in as admin: {admin['email']}")

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auths/signin",
                json={
                    "email": admin['email'],
                    "password": admin['password']
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                print(f"✓ Signed in as admin")
                return True
            else:
                print(f"✗ Failed to sign in: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ Error signing in: {e}")
            return False

    def create_users(self) -> List[Dict]:
        """Create all team users"""
        print("\n" + "="*70)
        print("Creating Team Users")
        print("="*70)

        results = []

        for user in self.config['users']:
            print(f"\nCreating: {user['name']} ({user['email']}) - {user['team'].upper()} Team")

            try:
                # Try signup endpoint first
                response = self.session.post(
                    f"{self.base_url}/api/v1/auths/signup",
                    json={
                        "email": user['email'],
                        "password": user['password'],
                        "name": user['name']
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    print(f"  ✓ User created successfully")
                    results.append({**user, 'status': 'created'})
                elif response.status_code == 400 and 'already' in response.text.lower():
                    print(f"  ℹ User already exists")
                    results.append({**user, 'status': 'exists'})
                else:
                    print(f"  ⚠ Signup returned {response.status_code}, trying admin API...")
                    # Try creating via admin API if we have admin token
                    if self.admin_token:
                        created = self.create_user_as_admin(user)
                        results.append({**user, 'status': 'created' if created else 'failed'})
                    else:
                        print(f"  ✗ Failed: No admin token available")
                        results.append({**user, 'status': 'failed'})

            except Exception as e:
                print(f"  ✗ Error: {e}")
                results.append({**user, 'status': 'failed'})

            time.sleep(1)

        return results

    def create_user_as_admin(self, user: Dict) -> bool:
        """Create user using admin privileges"""
        # This would require admin API endpoints
        # For now, we'll document that users need to be created through the UI
        # or by temporarily enabling signup
        return False

    def configure_models(self) -> bool:
        """Configure AI models in Open WebUI by directly updating the database"""
        print("\n" + "="*70)
        print("Configuring AI Model Connections")
        print("="*70)

        try:
            import subprocess

            # Python script to update database directly
            db_script = """
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
    data = {}

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

# Configure openai section
if 'openai' not in data:
    data['openai'] = {}

data['openai']['enable'] = True
data['openai']['api_base_urls'] = data['OPENAI_API_BASE_URLS']
data['openai']['api_keys'] = data['OPENAI_API_KEYS']

# CRITICAL: Configure api_configs with model_ids
data['openai']['api_configs'] = {
    '0': {
        'enable': True,
        'tags': [],
        'prefix_id': '',
        'model_ids': ['claude-haiku-4-5-20251001'],
        'connection_type': 'external',
        'auth_type': 'bearer'
    },
    '1': {
        'enable': True,
        'tags': [],
        'prefix_id': '',
        'model_ids': ['gpt-5.2-2025-12-11'],
        'connection_type': 'external',
        'auth_type': 'bearer'
    },
    '2': {
        'enable': True,
        'tags': [],
        'prefix_id': '',
        'model_ids': ['grok-4-latest'],
        'connection_type': 'external',
        'auth_type': 'bearer'
    },
    '3': {
        'enable': True,
        'tags': [],
        'prefix_id': '',
        'model_ids': ['gemini-3-pro-preview'],
        'connection_type': 'external',
        'auth_type': 'bearer'
    }
}

# Disable automatic model fetching
data['ENABLE_MODEL_FILTER'] = False

# Add models to model table
models = [
    {
        'id': 'claude-haiku-4-5-20251001',
        'name': 'Anthropic (Claude) - claude-haiku-4-5-20251001',
        'base_url': 'http://agentgateway:3000/anthropic/v1',
        'api_key': 'sk-anthropic'
    },
    {
        'id': 'gpt-5.2-2025-12-11',
        'name': 'OpenAI (GPT) - gpt-5.2-2025-12-11',
        'base_url': 'http://agentgateway:3000/openai/v1',
        'api_key': 'sk-openai'
    },
    {
        'id': 'grok-4-latest',
        'name': 'xAI (Grok) - grok-4-latest',
        'base_url': 'http://agentgateway:3000/xai/v1',
        'api_key': 'sk-xai'
    },
    {
        'id': 'gemini-3-pro-preview',
        'name': 'Gemini - gemini-3-pro-preview',
        'base_url': 'http://agentgateway:3000/gemini/v1',
        'api_key': 'sk-gemini'
    }
]

timestamp = int(time.time())
models_added = 0

for model_data in models:
    # Check if model already exists
    cursor.execute('SELECT id FROM model WHERE id = ?', (model_data['id'],))
    if cursor.fetchone():
        continue

    # Create model entry
    meta = json.dumps({
        'profile_image_url': '/static/favicon.png',
        'description': f"{model_data['name']} via AgentGateway",
        'capabilities': {},
        'position': models_added
    })

    params = json.dumps({
        'api_base_url': model_data['base_url'],
        'api_key': model_data['api_key'],
        'stream': True
    })

    cursor.execute(
        'INSERT INTO model (id, user_id, base_model_id, name, meta, params, created_at, updated_at, is_active, access_control) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (model_data['id'], '', model_data['id'], model_data['name'], meta, params, timestamp, timestamp, 1, json.dumps({'read': {'group_ids': [], 'user_ids': []}, 'write': {'group_ids': [], 'user_ids': []}}))
    )
    models_added += 1

# Save config
if result:
    cursor.execute('UPDATE config SET data = ?, updated_at = datetime("now") WHERE id = ?',
                   (json.dumps(data), config_id))
else:
    cursor.execute('INSERT INTO config (id, data, version, created_at, updated_at) VALUES (?, ?, 0, datetime("now"), datetime("now"))',
                   (config_id, json.dumps(data)))

conn.commit()
conn.close()

print(f"✓ Configured 4 API endpoints")
print(f"✓ Added {models_added} new models")
"""

            # Execute the script in the Open WebUI container
            result = subprocess.run(
                ["docker", "exec", "open-webui", "python3", "-c", db_script],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print("✓ Models configured successfully via database")
                print(result.stdout)
                return True
            else:
                print(f"✗ Failed to configure models: {result.stderr}")
                return False

        except Exception as e:
            print(f"✗ Error configuring models: {e}")
            return False

    def print_summary(self, user_results: List[Dict]):
        """Print initialization summary"""
        print("\n" + "="*70)
        print("INITIALIZATION SUMMARY")
        print("="*70)

        created = len([r for r in user_results if r['status'] == 'created'])
        exists = len([r for r in user_results if r['status'] == 'exists'])
        failed = len([r for r in user_results if r['status'] == 'failed'])

        print(f"\nUsers:")
        print(f"  ✓ Created:        {created}")
        print(f"  ℹ Already exist:  {exists}")
        print(f"  ✗ Failed:         {failed}")

        # Group by team
        teams = {}
        for user in user_results:
            team = user['team']
            if team not in teams:
                teams[team] = []
            teams[team].append(user)

        print("\n" + "="*70)
        print("USER ACCOUNTS BY TEAM")
        print("="*70)

        for team_name in sorted(teams.keys()):
            print(f"\n{team_name.upper()} TEAM:")
            print("-" * 50)
            for user in teams[team_name]:
                status_icon = {
                    'created': '✓',
                    'exists': 'ℹ',
                    'failed': '✗'
                }.get(user['status'], '?')

                print(f"  {status_icon} {user['name']}")
                print(f"      Email: {user['email']}")
                print(f"      Password: {user['password']}")

        print("\n" + "="*70)
        print("ACCESS INFORMATION")
        print("="*70)
        print(f"\nOpen WebUI URL: {self.base_url}")
        print(f"\nAdmin Credentials:")
        print(f"  Email:    {self.config['admin']['email']}")
        print(f"  Password: {self.config['admin']['password']}")
        print(f"\n⚠ IMPORTANT: Change the admin password after first login!")
        print()

    def run(self):
        """Main initialization routine"""
        print("="*70)
        print("Open WebUI Initialization")
        print("="*70)
        print()

        # Step 1: Wait for Open WebUI
        if not self.wait_for_openwebui():
            print("\n✗ Initialization failed: Open WebUI not ready")
            sys.exit(1)

        time.sleep(5)  # Give it a moment to fully start

        # Step 2: Create admin user
        print("\n" + "="*70)
        print("Creating Admin User")
        print("="*70)

        if not self.create_admin():
            print("\n⚠ Warning: Could not create/authenticate admin user")
            print("  You may need to create users manually through the UI")

        # Step 3: Create team users
        user_results = self.create_users()

        # Step 4: Configure models
        self.configure_models()

        # Step 5: Print summary
        self.print_summary(user_results)

        print("\n" + "="*70)
        print("Initialization Complete!")
        print("="*70)
        print()


def main():
    """Main entry point"""
    try:
        initializer = OpenWebUIInitializer()
        initializer.run()
    except Exception as e:
        print(f"\n✗ Initialization failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
