#!/usr/bin/env python3
"""
Analyze user activity from Jaeger traces
Generates reports showing which users are using which LLM providers
"""

import requests
import json
from collections import defaultdict
from datetime import datetime
import sys

# Configuration
JAEGER_URL = "http://localhost:16686/api/traces"
SERVICE_NAME = "agentgateway"

def fetch_traces(lookback="24h", limit=1000):
    """Fetch traces from Jaeger"""
    print(f"📡 Fetching traces from Jaeger (last {lookback})...")

    params = {
        "service": SERVICE_NAME,
        "lookback": lookback,
        "limit": limit
    }

    try:
        response = requests.get(JAEGER_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching traces: {e}")
        print(f"   Make sure Jaeger is running at {JAEGER_URL}")
        sys.exit(1)

def parse_traces(trace_data):
    """Parse traces and extract user activity"""
    user_stats = defaultdict(lambda: {
        "requests": 0,
        "providers": defaultdict(int),
        "methods": defaultdict(int),
        "total_duration_us": 0,
        "errors": 0,
        "status_codes": defaultdict(int)
    })

    total_traces = 0

    for item in trace_data:
        for trace in item.get("traces", []):
            total_traces += 1

            for span in trace.get("spans", []):
                # Extract information from span tags
                user_email = None
                provider = None
                route_name = None
                http_method = None
                http_status = None

                for tag in span.get("tags", []):
                    key = tag.get("key", "")
                    value = tag.get("value", "")

                    if key == "http.header.x-user-email":
                        user_email = value
                    elif key == "route.name":
                        route_name = value
                        # Extract provider from route name (e.g., "anthropic-claude" -> "anthropic")
                        if "-" in value:
                            provider = value.split("-")[0]
                        else:
                            provider = value
                    elif key == "http.method":
                        http_method = value
                    elif key == "http.status":
                        http_status = value

                # Only process spans with user information
                if user_email and user_email != "":
                    stats = user_stats[user_email]
                    stats["requests"] += 1
                    stats["total_duration_us"] += span.get("duration", 0)

                    if provider:
                        stats["providers"][provider] += 1

                    if http_method:
                        stats["methods"][http_method] += 1

                    if http_status:
                        stats["status_codes"][http_status] += 1
                        if int(http_status) >= 400:
                            stats["errors"] += 1

    return user_stats, total_traces

def print_report(user_stats, total_traces, lookback="24h"):
    """Print formatted user activity report"""
    if not user_stats:
        print("\n⚠️  No user activity found in traces")
        print("   This could mean:")
        print("   - Open WebUI is not sending X-User-Email headers")
        print("   - No requests have been made recently")
        print(f"   - Traces might be older than {lookback}")
        return

    print(f"\n{'='*70}")
    print(f"📊 USER ACTIVITY REPORT - Last {lookback}")
    print(f"{'='*70}")
    print(f"Total Traces: {total_traces}")
    print(f"Unique Users: {len(user_stats)}")
    print(f"{'='*70}\n")

    # Sort users by request count
    sorted_users = sorted(user_stats.items(), key=lambda x: x[1]["requests"], reverse=True)

    for idx, (user_email, stats) in enumerate(sorted_users, 1):
        avg_duration_ms = (stats["total_duration_us"] / stats["requests"] / 1000) if stats["requests"] > 0 else 0

        print(f"{idx}. {user_email}")
        print(f"   {'─'*66}")
        print(f"   Total Requests:     {stats['requests']}")
        print(f"   Avg Response Time:  {avg_duration_ms:.2f}ms")
        print(f"   Errors:             {stats['errors']} ({stats['errors']/stats['requests']*100:.1f}%)" if stats['requests'] > 0 else "   Errors:             0")

        if stats["providers"]:
            print(f"   Providers Used:")
            for provider, count in sorted(stats["providers"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats["requests"] * 100) if stats["requests"] > 0 else 0
                print(f"     • {provider.capitalize()}: {count} requests ({percentage:.1f}%)")

        if stats["status_codes"]:
            print(f"   Status Codes:")
            for code, count in sorted(stats["status_codes"].items()):
                print(f"     • {code}: {count} requests")

        print()

    # Summary statistics
    print(f"{'='*70}")
    print("📈 SUMMARY")
    print(f"{'='*70}\n")

    # Total requests by provider
    provider_totals = defaultdict(int)
    for stats in user_stats.values():
        for provider, count in stats["providers"].items():
            provider_totals[provider] += count

    if provider_totals:
        print("Provider Usage Distribution:")
        total_provider_requests = sum(provider_totals.values())
        for provider, count in sorted(provider_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_provider_requests * 100) if total_provider_requests > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"  {provider.capitalize():12} {bar} {count:4} ({percentage:.1f}%)")

    # Top users
    print(f"\nTop 5 Most Active Users:")
    for idx, (user_email, stats) in enumerate(sorted_users[:5], 1):
        print(f"  {idx}. {user_email} - {stats['requests']} requests")

    print(f"\n{'='*70}\n")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze user activity from AgentGateway Jaeger traces"
    )
    parser.add_argument(
        "--lookback",
        default="24h",
        help="Time range to analyze (e.g., 1h, 24h, 7d). Default: 24h"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Maximum number of traces to fetch. Default: 1000"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of formatted report"
    )

    args = parser.parse_args()

    # Fetch and parse traces
    trace_data = fetch_traces(lookback=args.lookback, limit=args.limit)
    user_stats, total_traces = parse_traces(trace_data)

    if args.json:
        # Output as JSON
        output = {
            "lookback": args.lookback,
            "total_traces": total_traces,
            "unique_users": len(user_stats),
            "users": {k: dict(v) for k, v in user_stats.items()}
        }
        print(json.dumps(output, indent=2))
    else:
        # Print formatted report
        print_report(user_stats, total_traces, args.lookback)

if __name__ == "__main__":
    main()
