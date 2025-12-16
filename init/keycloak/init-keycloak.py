#!/usr/bin/env python3
"""
Keycloak Initialization Script
===============================

This script configures Keycloak with:
- Realm (agentgateway)
- Users with team groups
- OpenID Connect client for Open WebUI
"""

import requests
import json
import time
import sys
from typing import Dict, Optional

KEYCLOAK_URL = "http://keycloak:8080"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"
REALM_CONFIG_FILE = "/app/realm-config.json"


class KeycloakConfigurator:
    """Handles Keycloak configuration"""

    def __init__(self, base_url: str, admin_user: str, admin_pass: str):
        self.base_url = base_url
        self.admin_user = admin_user
        self.admin_pass = admin_pass
        self.access_token: Optional[str] = None
        self.session = requests.Session()

    def wait_for_keycloak(self, max_attempts: int = 30) -> bool:
        """Wait for Keycloak to be ready"""
        print("Waiting for Keycloak to be ready...")

        for attempt in range(max_attempts):
            try:
                # Try to access the root endpoint (returns HTML)
                response = self.session.get(
                    f"{self.base_url}/",
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"✓ Keycloak is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass

            print(f"  Attempt {attempt + 1}/{max_attempts}... waiting")
            time.sleep(5)

        print("✗ Timeout waiting for Keycloak")
        return False

    def get_admin_token(self) -> bool:
        """Get admin access token"""
        print(f"\nAuthenticating as admin...")

        try:
            response = self.session.post(
                f"{self.base_url}/realms/master/protocol/openid-connect/token",
                data={
                    "client_id": "admin-cli",
                    "username": self.admin_user,
                    "password": self.admin_pass,
                    "grant_type": "password"
                },
                timeout=10
            )

            if response.status_code == 200:
                self.access_token = response.json()["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                })
                print(f"✓ Authenticated successfully")
                return True
            else:
                print(f"✗ Failed to authenticate: {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Error authenticating: {e}")
            return False

    def realm_exists(self, realm_name: str) -> bool:
        """Check if realm already exists"""
        try:
            response = self.session.get(
                f"{self.base_url}/admin/realms/{realm_name}",
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def create_realm(self, realm_config: Dict) -> bool:
        """Create realm with configuration"""
        realm_name = realm_config["realm"]

        if self.realm_exists(realm_name):
            print(f"ℹ Realm '{realm_name}' already exists, skipping creation")
            return True

        print(f"\nCreating realm: {realm_name}")

        try:
            response = self.session.post(
                f"{self.base_url}/admin/realms",
                json=realm_config,
                timeout=30
            )

            if response.status_code in [201, 409]:
                print(f"✓ Realm '{realm_name}' created")
                return True
            else:
                print(f"✗ Failed to create realm: {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Error creating realm: {e}")
            return False

    def get_realm_info(self, realm_name: str):
        """Get realm information"""
        try:
            response = self.session.get(
                f"{self.base_url}/admin/realms/{realm_name}",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def list_users(self, realm_name: str):
        """List users in realm"""
        try:
            response = self.session.get(
                f"{self.base_url}/admin/realms/{realm_name}/users",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []

    def list_clients(self, realm_name: str):
        """List clients in realm"""
        try:
            response = self.session.get(
                f"{self.base_url}/admin/realms/{realm_name}/clients",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []

    def get_client_secret(self, realm_name: str, client_id: str) -> Optional[str]:
        """Get client secret"""
        try:
            # Get client UUID
            clients = self.list_clients(realm_name)
            client = next((c for c in clients if c["clientId"] == client_id), None)

            if not client:
                return None

            # Get client secret
            response = self.session.get(
                f"{self.base_url}/admin/realms/{realm_name}/clients/{client['id']}/client-secret",
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get("value")
            return None
        except:
            return None

    def print_summary(self, realm_name: str):
        """Print configuration summary"""
        print("\n" + "="*70)
        print("KEYCLOAK CONFIGURATION SUMMARY")
        print("="*70)

        realm_info = self.get_realm_info(realm_name)
        if realm_info:
            print(f"\nRealm: {realm_info['realm']}")
            print(f"Display Name: {realm_info.get('displayName', 'N/A')}")
            print(f"Enabled: {realm_info.get('enabled', False)}")

        print("\nUsers:")
        users = self.list_users(realm_name)
        for user in users:
            print(f"  • {user.get('username')} ({user.get('email')})")

        print("\nClients:")
        clients = self.list_clients(realm_name)
        for client in clients:
            if client['clientId'] in ['open-webui']:
                secret = self.get_client_secret(realm_name, client['clientId'])
                print(f"  • {client['clientId']}")
                if secret:
                    print(f"    Client Secret: {secret}")

        print("\n" + "="*70)
        print("ACCESS INFORMATION")
        print("="*70)
        print(f"\nKeycloak Admin Console: http://localhost:8090")
        print(f"  Username: {ADMIN_USERNAME}")
        print(f"  Password: {ADMIN_PASSWORD}")
        print()
        print(f"Realm: {realm_name}")
        print(f"  Login URL: http://localhost:8090/realms/{realm_name}/account")
        print()
        print("Open WebUI OIDC Configuration:")
        print(f"  Issuer: http://localhost:8090/realms/{realm_name}")
        print(f"  Client ID: open-webui")

        secret = self.get_client_secret(realm_name, "open-webui")
        if secret:
            print(f"  Client Secret: {secret}")

        print(f"  Authorization URL: http://localhost:8090/realms/{realm_name}/protocol/openid-connect/auth")
        print(f"  Token URL: http://localhost:8090/realms/{realm_name}/protocol/openid-connect/token")
        print(f"  UserInfo URL: http://localhost:8090/realms/{realm_name}/protocol/openid-connect/userinfo")
        print()
        print("="*70)
        print()

    def run(self):
        """Main initialization routine"""
        print("="*70)
        print("Keycloak Initialization")
        print("="*70)
        print()

        # Step 1: Wait for Keycloak
        if not self.wait_for_keycloak():
            print("\n✗ Initialization failed: Keycloak not ready")
            sys.exit(1)

        time.sleep(5)

        # Step 2: Authenticate
        if not self.get_admin_token():
            print("\n✗ Initialization failed: Could not authenticate")
            sys.exit(1)

        # Step 3: Load realm configuration
        print(f"\nLoading realm configuration from {REALM_CONFIG_FILE}...")
        try:
            with open(REALM_CONFIG_FILE, 'r') as f:
                realm_config = json.load(f)
            print(f"✓ Configuration loaded")
        except Exception as e:
            print(f"✗ Failed to load configuration: {e}")
            sys.exit(1)

        # Step 4: Create realm
        if not self.create_realm(realm_config):
            print("\n⚠ Warning: Could not create realm")

        # Step 5: Print summary
        self.print_summary(realm_config["realm"])

        print("="*70)
        print("Initialization Complete!")
        print("="*70)
        print()


def main():
    """Main entry point"""
    try:
        configurator = KeycloakConfigurator(
            KEYCLOAK_URL,
            ADMIN_USERNAME,
            ADMIN_PASSWORD
        )
        configurator.run()
    except Exception as e:
        print(f"\n✗ Initialization failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
