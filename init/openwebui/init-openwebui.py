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
        """Configure AI models in Open WebUI"""
        print("\n" + "="*70)
        print("Configuring AI Model Connections")
        print("="*70)

        if not self.admin_token:
            print("✗ No admin token available, cannot configure connections")
            return False

        # Configure connections for each provider
        connections = [
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

        success_count = 0
        for conn in connections:
            print(f"\nConfiguring: {conn['name']}")
            print(f"  URL: {conn['url']}")
            print(f"  Models: {', '.join(conn['models'])}")

            try:
                # Create connection via API
                payload = {
                    "url": conn['url'],
                    "key": conn['api_key'],
                    "models": conn['models']
                }

                response = self.session.post(
                    f"{self.base_url}/api/v1/configs/connections",
                    json=payload,
                    timeout=10
                )

                if response.status_code in [200, 201]:
                    print(f"  ✓ Connection configured successfully")
                    success_count += 1
                elif response.status_code == 409 or "exists" in response.text.lower():
                    print(f"  ℹ Connection already exists")
                    success_count += 1
                else:
                    print(f"  ⚠ API returned {response.status_code}: {response.text[:100]}")

            except Exception as e:
                print(f"  ✗ Error: {e}")

            time.sleep(1)

        print(f"\n✓ Configured {success_count}/{len(connections)} connections")
        return success_count > 0

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
