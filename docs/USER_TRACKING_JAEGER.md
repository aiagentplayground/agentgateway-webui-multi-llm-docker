# User Tracking via Jaeger Traces

Since AgentGateway doesn't support custom Prometheus metrics labels in the current version, we can track user activity through **Jaeger distributed tracing**, which is already configured and running.

## How It Works

```
User → Open WebUI → AgentGateway → LLM Provider
        (adds headers)    ↓
                    (creates trace)
                          ↓
                       Jaeger
                          ↓
                   (search/analyze)
```

AgentGateway sends all requests to Jaeger with:
- Request details (method, path, status)
- Timing information
- Request headers (including user information)
- Provider information

## Viewing User Activity in Jaeger

### 1. Access Jaeger UI

Open: **http://localhost:16686**

### 2. Search for User Activity

**By User Email (if Open WebUI passes it):**
1. Service: Select `agentgateway`
2. Tags: Add `http.header.x-user-email=sarah.johnson@example.com`
3. Click "Find Traces"

**By Time Range:**
1. Service: `agentgateway`
2. Lookback: Last Hour / Last 24 Hours
3. Max Duration / Min Duration: Filter by response time

**By Provider:**
1. Service: `agentgateway`
2. Tags: `route.name=anthropic-claude` or `route.name=openai-gpt`

### 3. Analyze Traces

Each trace shows:
- **Duration**: How long the request took
- **Status**: Success/failure
- **Provider**: Which LLM was used (Anthropic, OpenAI, xAI, Gemini)
- **Request Headers**: Including user information
- **Response Details**: Status codes, errors

## Creating User Reports

### Export Trace Data

1. Use Jaeger's API to query traces:

```bash
# Get traces for the last hour
curl 'http://localhost:16686/api/traces?service=agentgateway&limit=100&lookback=1h' | jq .
```

2. Filter by user tags:

```bash
# Get traces for specific user
curl 'http://localhost:16686/api/traces?service=agentgateway&tags={"http.header.x-user-email":"sarah.johnson@example.com"}&limit=100' | jq .
```

### Analyze with Scripts

Create a Python script to aggregate user activity:

```python
#!/usr/bin/env python3
import requests
import json
from collections import defaultdict
from datetime import datetime, timedelta

# Query Jaeger for recent traces
jaeger_url = "http://localhost:16686/api/traces"
params = {
    "service": "agentgateway",
    "lookback": "24h",
    "limit": 1000
}

response = requests.get(jaeger_url, params=params)
data = response.json()

# Aggregate by user
user_stats = defaultdict(lambda: {
    "requests": 0,
    "providers": defaultdict(int),
    "total_duration": 0,
    "errors": 0
})

for trace_data in data.get("data", []):
    for trace in trace_data.get("traces", []):
        for span in trace.get("spans", []):
            # Extract user email from tags
            user_email = None
            provider = None

            for tag in span.get("tags", []):
                if tag["key"] == "http.header.x-user-email":
                    user_email = tag["value"]
                elif tag["key"] == "route.name":
                    provider = tag["value"]
                elif tag["key"] == "http.status" and int(tag["value"]) >= 400:
                    user_stats[user_email]["errors"] += 1

            if user_email:
                user_stats[user_email]["requests"] += 1
                user_stats[user_email]["total_duration"] += span["duration"]

                if provider:
                    user_stats[user_email]["providers"][provider] += 1

# Print report
print("User Activity Report (Last 24h)")
print("=" * 60)
for user, stats in sorted(user_stats.items(), key=lambda x: x[1]["requests"], reverse=True):
    print(f"\n{user}:")
    print(f"  Total Requests: {stats['requests']}")
    print(f"  Avg Duration: {stats['total_duration'] / stats['requests'] / 1000:.2f}ms")
    print(f"  Errors: {stats['errors']}")
    print(f"  Providers:")
    for provider, count in stats["providers"].items():
        print(f"    - {provider}: {count} requests")
```

Save as `scripts/analyze-user-activity.py` and run:
```bash
python3 scripts/analyze-user-activity.py
```

## Alternative: Prometheus Metrics from Logs

We can also create custom Prometheus metrics by parsing AgentGateway logs.

### 1. Install mtail (Log Parser)

```bash
# macOS
brew install mtail

# Linux
wget https://github.com/google/mtail/releases/download/v3.0.0-rc52/mtail_v3.0.0-rc52_linux_amd64
chmod +x mtail_v3.0.0-rc52_linux_amd64
sudo mv mtail_v3.0.0-rc52_linux_amd64 /usr/local/bin/mtail
```

### 2. Create mtail Configuration

Create `monitoring/mtail/agentgateway.mtail`:

```mtail
# Parse AgentGateway logs and expose as Prometheus metrics

counter requests_by_user by user_email, route, status

# Parse log lines like:
# request gateway=bind/3000 listener=agentgateway src.addr=127.0.0.1:42066
# http.method=POST http.path=/anthropic/v1/messages http.header.x-user-email=sarah.johnson@example.com
# http.status=200 trace.id=abc123

/request gateway=\S+ listener=\S+ .* http\.header\.x-user-email=(?P<user_email>\S+) .* route\.name=(?P<route>\S+) .* http\.status=(?P<status>\d+)/ {
  requests_by_user[$user_email][$route][$status]++
}
```

### 3. Run mtail

```bash
# In docker-compose.yml, add mtail service
mtail:
  image: mtail/mtail:latest
  command: -progs /etc/mtail -logs /var/log/agentgateway.log -port 3903
  ports:
    - "3903:3903"
  volumes:
    - ./monitoring/mtail:/etc/mtail
    - agentgateway-logs:/var/log
```

### 4. Configure Prometheus to Scrape mtail

Add to `monitoring/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'mtail'
    static_configs:
      - targets: ['mtail:3903']
```

Now user metrics will be available at:
```promql
requests_by_user{user_email="sarah.johnson@example.com"}
```

## Simple Logging Approach

For immediate visibility without additional tools, enable request logging in AgentGateway and grep the logs:

### View Requests by User

```bash
# See all requests from a specific user
docker-compose logs agentgateway | grep "sarah.johnson@example.com"

# Count requests per user
docker-compose logs agentgateway | grep "x-user-email" | awk '{print $NF}' | sort | uniq -c

# Requests by provider
docker-compose logs agentgateway | grep "route.name" | awk '{print $NF}' | sort | uniq -c
```

### Create Daily Reports

```bash
#!/bin/bash
# scripts/daily-user-report.sh

echo "Daily User Activity Report - $(date)"
echo "======================================"
echo ""

echo "Top 10 Users by Request Count:"
docker-compose logs --since 24h agentgateway 2>&1 | \
  grep -o 'http\.header\.x-user-email=[^ ]*' | \
  cut -d= -f2 | \
  sort | uniq -c | sort -rn | head -10

echo ""
echo "Requests by Provider:"
docker-compose logs --since 24h agentgateway 2>&1 | \
  grep -o 'route\.name=[^ ]*' | \
  cut -d= -f2 | \
  sort | uniq -c | sort -rn

echo ""
echo "Errors by User:"
docker-compose logs --since 24h agentgateway 2>&1 | \
  grep "http\.status=[45]" | \
  grep -o 'http\.header\.x-user-email=[^ ]*' | \
  cut -d= -f2 | \
  sort | uniq -c | sort -rn
```

## Configuring Open WebUI to Send User Headers

Open WebUI needs to pass user information in headers. Add this to your Open WebUI configuration or custom middleware:

### Option 1: Environment Variable

Add to `docker-compose.yml`:

```yaml
open-webui:
  environment:
    - CUSTOM_REQUEST_HEADERS=X-User-Email:${USER_EMAIL},X-User-Id:${USER_ID}
```

### Option 2: Custom Function in Open WebUI

If Open WebUI supports functions or extensions, create a function that adds headers:

```javascript
// Open WebUI function to add user headers
export default async function addUserHeaders(request, user) {
  request.headers['X-User-Email'] = user.email;
  request.headers['X-User-Id'] = user.id;
  request.headers['X-User-Name'] = user.name;
  request.headers['X-User-Role'] = user.role;
  return request;
}
```

## Summary

While AgentGateway doesn't support custom Prometheus labels directly, we have several options for user tracking:

1. **✅ Jaeger Traces** (Already Working)
   - View individual requests by user
   - Analyze performance per user
   - Export data via API

2. **✅ Log Analysis** (Simple, No Setup)
   - Parse logs with grep/awk
   - Create daily reports with bash scripts

3. **🔧 mtail** (Advanced, Prometheus Integration)
   - Converts logs to Prometheus metrics
   - Enables Grafana dashboards

4. **🔧 Custom Exporter** (Most Flexible)
   - Python service that reads Jaeger API
   - Exposes user metrics for Prometheus

**Recommended Approach:**
- Start with **Jaeger traces** for immediate visibility
- Use **log analysis scripts** for daily reports
- If you need Grafana dashboards, implement **mtail** or a **custom exporter**

For questions, run:
```bash
./scripts/test-user-tracking.sh
```

This will verify that traces are being captured and provide next steps.
