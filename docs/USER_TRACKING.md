# User and Team Tracking in AgentGateway

This document explains how to track which users and teams are using which LLM providers through the AgentGateway platform with Keycloak SSO integration.

## ⚠️ Important Update

AgentGateway's current version doesn't support custom Prometheus metric labels directly. Instead, we use **Jaeger distributed tracing** for user tracking, which provides even better visibility into individual requests.

**📖 See the complete guide:** [USER_TRACKING_JAEGER.md](USER_TRACKING_JAEGER.md)

## Overview

The platform supports user and team analytics through:
- **Distributed Tracing**: Jaeger captures all requests with user information
- **Request Analysis**: Python scripts analyze traces and generate reports
- **Log Analysis**: Parse AgentGateway logs for user activity
- **Optional**: Advanced setup with mtail for Prometheus integration

## Architecture

```
User → Keycloak (SSO) → Open WebUI → AgentGateway → LLM Providers
                           ↓              ↓
                    (adds headers)   (sends traces)
                                         ↓
                                      Jaeger
                                         ↓
                                  Python Scripts
                                         ↓
                                      Reports
```

## Quick Start

### 1. Verify Jaeger is Running

```bash
docker-compose ps jaeger
# Should show "Up"
```

### 2. Generate User Activity Report

```bash
# Analyze last 24 hours
python3 scripts/analyze-user-activity.py

# Analyze last hour
python3 scripts/analyze-user-activity.py --lookback 1h

# Get JSON output
python3 scripts/analyze-user-activity.py --json
```

### 3. View Traces in Jaeger UI

Open **http://localhost:16686** and search for:
- Service: `agentgateway`
- Tags: `http.header.x-user-email=user@example.com`

## Configuration

### 1. AgentGateway Configuration

AgentGateway is already configured to send traces to Jaeger:

```yaml
config:
  tracing:
    otlpEndpoint: http://jaeger:4317
    randomSampling: true  # Captures all requests
```

**This automatically captures:**
- Request method, path, and headers (including user info)
- Response status and duration
- Provider information
- Error details

### 2. Open WebUI Configuration

Open WebUI needs to be configured to pass user identity in request headers when making calls to AgentGateway.

#### Option A: Environment Variables (Automatic)

Add to `docker-compose.yml` under the `open-webui` service:

```yaml
environment:
  - ENABLE_USER_HEADERS=true
  - USER_HEADER_PREFIX=X-User-
```

This automatically adds:
- `X-User-Email: user@example.com`
- `X-User-Id: 12345`
- `X-User-Name: John Doe`
- `X-User-Role: user`

#### Option B: Custom Middleware (Advanced)

Create a custom middleware in Open WebUI that injects user headers:

```python
# In Open WebUI backend, add to middleware
async def add_user_headers(request: Request, call_next):
    if hasattr(request.state, 'user'):
        user = request.state.user
        request.headers['X-User-Email'] = user.email
        request.headers['X-User-Id'] = str(user.id)
        request.headers['X-User-Name'] = user.name
        request.headers['X-User-Role'] = user.role
    response = await call_next(request)
    return response
```

### 3. Keycloak User Groups

Users in Keycloak are organized into teams (groups):
- **Marketing**: sarah.johnson, mike.chen
- **Platform**: alex.rivera, jordan.kim
- **Security**: taylor.morgan

Team membership is extracted from the user's email domain or Keycloak group membership.

## Available Metrics

### Prometheus Metrics with User Labels

All AgentGateway metrics now include user labels:

```promql
# Request rate by user
agentgateway_requests_total{user_email="sarah.johnson@example.com", provider="anthropic"}

# Response time by user
agentgateway_request_duration_seconds{user_email="alex.rivera@example.com", provider="openai"}

# Token usage by user
agentgateway_tokens_used_total{user_email="taylor.morgan@example.com", provider="gemini"}
```

### Example PromQL Queries

**Total requests per user (24h):**
```promql
sum(increase(agentgateway_requests_total{user_email!=""}[24h])) by (user_email)
```

**Requests by provider and user:**
```promql
sum(rate(agentgateway_requests_total{user_email!=""}[5m])) by (user_email, provider)
```

**Team usage (by email domain):**
```promql
sum(increase(agentgateway_requests_total[24h])) by (user_email)
```

**Top 10 users by request count:**
```promql
topk(10, sum(increase(agentgateway_requests_total{user_email!=""}[24h])) by (user_email))
```

**Average response time by user:**
```promql
histogram_quantile(0.95,
  sum(rate(agentgateway_request_duration_seconds_bucket{user_email!=""}[5m]))
  by (user_email, le)
)
```

## Grafana Dashboards

### User & Team Analytics Dashboard

Access at: **http://localhost:3100** → **Dashboards** → **LLM Monitoring** → **User & Team Analytics**

**Features:**
1. **Requests per Second by User** - Real-time request rate per user
2. **Total Requests (24h) by User** - Daily request counts
3. **Provider Usage Distribution** - Which LLM providers are most popular
4. **User Activity Distribution** - Which users are most active
5. **User Activity by Provider (Hourly)** - Stacked bar chart showing hourly usage
6. **Detailed Activity Table** - Complete breakdown of requests by user and provider
7. **Response Time by User** - Performance metrics per user (p95)
8. **Provider Usage Share Over Time** - Trending provider popularity

**Dashboard Variables:**
- `$user` - Filter by specific user(s)
- `$provider` - Filter by specific provider(s)

### Creating Custom Team Views

To create team-specific dashboards:

1. **By Email Domain:**
   ```promql
   sum(rate(agentgateway_requests_total{user_email=~".*@marketing\\..*"}[5m]))
   ```

2. **By User Group:**
   ```promql
   sum(rate(agentgateway_requests_total{
     user_email=~"sarah\\.johnson|mike\\.chen"
   }[5m]))
   ```

3. **Team Comparison:**
   ```promql
   sum(increase(agentgateway_requests_total[24h])) by (user_email)
   * on(user_email) group_left(team)
   user_team_info{team=~"marketing|platform|security"}
   ```

## Usage Examples

### View User Activity

1. Open Grafana: http://localhost:3100
2. Navigate to: **Dashboards** → **LLM Monitoring** → **User & Team Analytics**
3. Use the dropdown filters to select specific users or providers
4. View real-time and historical usage patterns

### Track Provider Preferences by Team

**Marketing Team Anthropic Usage:**
```promql
sum(increase(agentgateway_requests_total{
  user_email=~"sarah\\.johnson|mike\\.chen",
  provider="anthropic"
}[24h]))
```

**Platform Team OpenAI Usage:**
```promql
sum(increase(agentgateway_requests_total{
  user_email=~"alex\\.rivera|jordan\\.kim",
  provider="openai"
}[24h]))
```

### Generate User Reports

Use Grafana's **Export** feature to generate reports:
1. Set time range (e.g., Last 7 days)
2. Select user(s) from dropdown
3. Click **Share** → **Export** → **PDF**

## Cost Tracking by User

To track costs per user, you can create alerts and calculations:

### Estimated Cost Calculation

```promql
# Assuming token costs (example rates)
(
  sum(increase(agentgateway_tokens_used_total{provider="anthropic"}[24h])) by (user_email)
  * 0.000015  # $0.015 per 1K tokens
) + (
  sum(increase(agentgateway_tokens_used_total{provider="openai"}[24h])) by (user_email)
  * 0.000030  # $0.03 per 1K tokens
)
```

### Setting Budget Alerts

Create alerts in Grafana when users exceed thresholds:

1. **Go to Alerting** → **Alert Rules** → **New Alert Rule**
2. **Query:**
   ```promql
   sum(increase(agentgateway_requests_total{
     user_email="sarah.johnson@example.com"
   }[1h])) > 100
   ```
3. **Alert when:** User exceeds 100 requests per hour
4. **Notification:** Send to Slack/Email

## Security and Privacy

### Data Retention

Configure Prometheus data retention in `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

storage:
  tsdb:
    retention_time: 30d  # Keep 30 days of data
```

### GDPR Compliance

To anonymize user data:

1. **Hash user emails** in AgentGateway:
   ```yaml
   metrics:
     customLabels:
       - name: user_id_hash
         header: X-User-Email
         transform: sha256  # Hash the email
   ```

2. **Remove PII** after retention period:
   ```bash
   # Drop user data older than 30 days
   curl -X POST \
     -g 'http://localhost:9090/api/v1/admin/tsdb/delete_series?match[]={user_email!=""}&start=0&end=<30-days-ago-timestamp>'
   ```

### Access Control

Restrict dashboard access in Grafana:
1. **Settings** → **Users and Access**
2. Create role: "Analytics Viewer"
3. Assign users who can view analytics dashboards

## Testing User Tracking

### Verify Headers Are Being Sent

Use curl to test that headers are passed:

```bash
# Make request with user headers
curl -X POST http://localhost:3000/anthropic/v1/messages \
  -H "Content-Type: application/json" \
  -H "X-User-Email: test@example.com" \
  -H "X-User-Id: 12345" \
  -H "X-User-Name: Test User" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

### Check Prometheus Metrics

Verify user labels appear in metrics:

```bash
# Query Prometheus for user metrics
curl 'http://localhost:9090/api/v1/query?query=agentgateway_requests_total{user_email!=""}'
```

Expected response:
```json
{
  "metric": {
    "__name__": "agentgateway_requests_total",
    "user_email": "test@example.com",
    "user_name": "Test User",
    "provider": "anthropic"
  },
  "value": [1702392000, "5"]
}
```

### View in Grafana

1. Open Grafana: http://localhost:3100
2. Navigate to **Explore**
3. Run query:
   ```promql
   agentgateway_requests_total{user_email!=""}
   ```
4. Verify user labels appear in results

## Troubleshooting

### Headers Not Being Captured

**Issue:** User labels are empty in Prometheus

**Solutions:**
1. Check Open WebUI is sending headers:
   ```bash
   docker-compose logs open-webui | grep -i "x-user"
   ```

2. Verify AgentGateway configuration:
   ```bash
   docker-compose exec agentgateway cat /etc/agentgateway/agentgateway.yaml
   ```

3. Restart services:
   ```bash
   docker-compose restart agentgateway prometheus grafana
   ```

### Dashboard Shows No Data

**Issue:** User & Team Analytics dashboard is empty

**Solutions:**
1. Verify Prometheus is scraping AgentGateway:
   ```bash
   curl http://localhost:9090/api/v1/targets
   ```

2. Check if metrics exist:
   ```bash
   curl http://localhost:15020/metrics | grep agentgateway_requests_total
   ```

3. Ensure time range is correct in Grafana (try "Last 24 hours")

### User Identity Missing

**Issue:** `user_email` label is empty

**Solutions:**
1. Verify Keycloak authentication is working
2. Check Open WebUI session contains user info
3. Ensure middleware is enabled in Open WebUI
4. Test with curl to verify headers work independently

## Advanced Configuration

### Team Mapping from Email Domains

Create recording rules in Prometheus to map emails to teams:

```yaml
# prometheus.yml
rule_files:
  - /etc/prometheus/rules/*.yml

# /etc/prometheus/rules/team_mapping.yml
groups:
  - name: team_mapping
    rules:
      - record: user:team:mapping
        expr: |
          label_replace(
            agentgateway_requests_total{user_email=~".*@marketing\\..*"},
            "team", "marketing", "user_email", ".*"
          )
```

### Real-time Alerts for Anomalies

Alert when user activity is unusual:

```yaml
# /etc/prometheus/rules/user_alerts.yml
groups:
  - name: user_alerts
    rules:
      - alert: UnusualUserActivity
        expr: |
          rate(agentgateway_requests_total[5m])
          > 5 * avg_over_time(rate(agentgateway_requests_total[5m])[1h:5m])
        for: 10m
        annotations:
          summary: "Unusual activity from {{ $labels.user_email }}"
          description: "User {{ $labels.user_email }} request rate is 5x normal"
```

## Summary

With user and team tracking enabled, you can now:
- ✅ Monitor which users are using which LLM providers
- ✅ Track usage patterns by team
- ✅ Identify power users and inactive users
- ✅ Optimize costs by analyzing provider preferences
- ✅ Generate reports for management and billing
- ✅ Set up alerts for unusual activity or budget overruns

For questions or issues, check the logs:
```bash
docker-compose logs -f agentgateway prometheus grafana
```
