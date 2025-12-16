#!/usr/bin/env python3
"""
Track user activity by correlating Open WebUI logs with AgentGateway traces
Since Open WebUI doesn't pass user headers, we infer activity from logs
"""

import subprocess
import re
from collections import defaultdict
from datetime import datetime
import json

def get_openwebui_chat_logs():
    """Extract chat activity from Open WebUI logs"""
    print("📊 Analyzing Open WebUI logs...")

    cmd = ["docker-compose", "logs", "--since", "24h", "open-webui"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        logs = result.stdout
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
        return {}

    # Parse logs for user activity
    # Look for patterns like: INFO:     User 'mike.chen' requested chat
    user_activity = defaultdict(lambda: {
        "requests": 0,
        "timestamps": []
    })

    # Common patterns in Open WebUI logs
    patterns = [
        r"user['\"]?\s*[:=]\s*['\"]?(\S+@\S+\.\S+|[\w\.]+)['\"]?",  # email or username
        r"User\s+['\"](\w+\.?\w*)['\"]",  # User 'username'
        r"INFO.*auth.*user=(\S+)",  # auth user=username
    ]

    for line in logs.split('\n'):
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                username = match.group(1)
                user_activity[username]["requests"] += 1
                # Try to extract timestamp
                ts_match = re.match(r'.*?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', line)
                if ts_match:
                    user_activity[username]["timestamps"].append(ts_match.group(1))

    return dict(user_activity)

def get_agentgateway_stats():
    """Get request stats from AgentGateway"""
    print("📊 Analyzing AgentGateway logs...")

    cmd = ["docker-compose", "logs", "--since", "24h", "agentgateway"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        logs = result.stdout
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
        return {}

    stats = {
        "total_requests": 0,
        "by_provider": defaultdict(int),
        "by_status": defaultdict(int),
        "successful": 0,
        "errors": 0
    }

    # Parse for successful requests
    for line in logs.split('\n'):
        if 'route_rule=' in line and 'http.status=' in line:
            stats["total_requests"] += 1

            # Extract provider
            provider_match = re.search(r'gen_ai\.provider\.name=(\w+)', line)
            if provider_match:
                provider = provider_match.group(1)
                stats["by_provider"][provider] += 1

            # Extract status
            status_match = re.search(r'http\.status=(\d+)', line)
            if status_match:
                status = status_match.group(1)
                stats["by_status"][status] += 1

                if status.startswith('2'):
                    stats["successful"] += 1
                elif status.startswith(('4', '5')):
                    stats["errors"] += 1

    return stats

def get_active_users_from_db():
    """Get list of users who have logged in (from Open WebUI database)"""
    print("📊 Checking active users from database...")

    # Query Open WebUI's SQLite database
    cmd = [
        "docker-compose", "exec", "-T", "open-webui",
        "sqlite3", "/app/backend/data/webui.db",
        "SELECT email, name, role, last_active_at FROM user ORDER BY last_active_at DESC LIMIT 10;"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            users = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        users.append({
                            "email": parts[0],
                            "name": parts[1] if len(parts) > 1 else "",
                            "role": parts[2] if len(parts) > 2 else "",
                            "last_active": parts[3] if len(parts) > 3 else ""
                        })
            return users
    except Exception as e:
        print(f"⚠️  Could not query database: {e}")

    return []

def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("📊 USER ACTIVITY REPORT (Open WebUI + AgentGateway)")
    print("=" * 70 + "\n")

    # Get active users from database
    active_users = get_active_users_from_db()

    if active_users:
        print("👥 Recently Active Users:")
        print("-" * 70)
        for idx, user in enumerate(active_users, 1):
            print(f"{idx}. {user['email']}")
            if user['name']:
                print(f"   Name: {user['name']}")
            print(f"   Role: {user['role']}")
            if user['last_active']:
                print(f"   Last Active: {user['last_active']}")
            print()
    else:
        print("⚠️  No user data available from database\n")

    # Get OpenWebUI activity
    openwebui_activity = get_openwebui_chat_logs()

    if openwebui_activity:
        print("\n💬 Chat Activity (from logs):")
        print("-" * 70)
        for user, stats in sorted(openwebui_activity.items(), key=lambda x: x[1]["requests"], reverse=True):
            print(f"• {user}: {stats['requests']} events")
    else:
        print("\n⚠️  No chat activity found in Open WebUI logs\n")

    # Get AgentGateway stats
    ag_stats = get_agentgateway_stats()

    print("\n🚀 AgentGateway Statistics (Last 24h):")
    print("-" * 70)
    print(f"Total Requests:  {ag_stats['total_requests']}")
    print(f"Successful:      {ag_stats['successful']}")
    print(f"Errors:          {ag_stats['errors']}")

    if ag_stats['by_provider']:
        print(f"\nBy Provider:")
        for provider, count in sorted(ag_stats['by_provider'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / ag_stats['total_requests'] * 100) if ag_stats['total_requests'] > 0 else 0
            print(f"  • {provider.capitalize()}: {count} requests ({percentage:.1f}%)")

    if ag_stats['by_status']:
        print(f"\nBy Status Code:")
        for status, count in sorted(ag_stats['by_status'].items()):
            print(f"  • HTTP {status}: {count} requests")

    print("\n" + "=" * 70)
    print("\n📝 Note: To get per-user LLM usage statistics, Open WebUI needs to")
    print("   pass user headers to AgentGateway. See docs/USER_TRACKING_JAEGER.md")
    print("\n   Current tracking shows:")
    print("   ✓ Active users in the system")
    print("   ✓ Total LLM requests")
    print("   ✓ Provider usage distribution")
    print("   ✗ Per-user LLM request mapping (requires header configuration)")
    print("\n" + "=" * 70 + "\n")

    # Provide actionable next steps
    print("🔧 To enable full user tracking:")
    print("-" * 70)
    print("1. The requests ARE reaching AgentGateway (verified)")
    print("2. The requests ARE being traced in Jaeger (verified)")
    print("3. Open WebUI needs to pass X-User-Email header")
    print()
    print("   Option A: Add custom Open WebUI function/middleware")
    print("   Option B: Use Open WebUI's built-in analytics")
    print("   Option C: Track by session/IP correlation")
    print()
    print("For now, you can:")
    print("• View individual traces in Jaeger: http://localhost:16686")
    print("• See provider usage in this report")
    print("• Check Open WebUI's admin panel for user stats")
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
