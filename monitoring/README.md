# AgentGateway Monitoring Setup

This directory contains the monitoring infrastructure for tracking LLM usage, costs, and performance across all AI providers (Anthropic, OpenAI, xAI, Gemini).

## Architecture

- **Prometheus**: Metrics collection and storage (scrapes AgentGateway metrics on port 15020)
- **Grafana**: Visualization and dashboarding (accessible on port 3100)
- **AgentGateway**: Exposes OpenTelemetry metrics for all LLM interactions

## Quick Start

1. Start the entire stack:
```bash
docker-compose up -d
```

2. Access the services:
   - **Grafana**: http://localhost:3100
     - Username: `admin`
     - Password: `admin`
   - **Prometheus**: http://localhost:9090
   - **AgentGateway Metrics**: http://localhost:15020/metrics

3. The dashboards will be automatically loaded in Grafana under the "LLM Monitoring" folder

## Available Dashboards

### 1. Global LLM Cost Dashboard
**File**: `dashboards/global-cost-dashboard.json`

Unified view across all LLM providers showing:
- Total requests, tokens, and cost rate across all providers
- Request rate comparison by provider (stacked timeseries)
- Request and token distribution (pie charts)
- Cost breakdown by provider with input/output split
- Average latency comparison

**Use this dashboard for:**
- Executive overview of LLM spending
- Comparing costs across different providers
- Identifying which provider/model is most cost-effective
- Budget tracking and forecasting

### 2. Anthropic Dashboard
**File**: `dashboards/anthropic-dashboard.json`

Detailed metrics for Anthropic Claude models:
- Request metrics (total, rate by model, latency)
- Token usage (input/output breakdown, percentiles)
- Performance metrics (latency percentiles, time per token)
- Cost estimation (~$3/M input, ~$15/M output for Haiku)

### 3. OpenAI Dashboard
**File**: `dashboards/openai-dashboard.json`

Detailed metrics for OpenAI GPT models:
- Request metrics (total, rate by model, latency)
- Token usage (input/output breakdown, percentiles)
- Performance metrics (latency percentiles, time per token)
- Cost estimation (~$0.15/M input, ~$0.60/M output for GPT-4o-mini)

### 4. xAI (Grok) Dashboard
**File**: `dashboards/xai-dashboard.json`

Detailed metrics for xAI Grok models:
- Request metrics (total, rate by model, latency)
- Token usage (input/output breakdown, percentiles)
- Performance metrics (latency percentiles, time per token)
- Cost estimation (~$2/M input, ~$10/M output)

### 5. Gemini Dashboard
**File**: `dashboards/gemini-dashboard.json`

Detailed metrics for Google Gemini models:
- Request metrics (total, rate by model, latency)
- Token usage (input/output breakdown, percentiles)
- Performance metrics (latency percentiles, time per token)
- Cost estimation (~$0.075/M input, ~$0.30/M output for Gemini 1.5 Flash)

## Key Metrics Explained

### Request Metrics
- **Total Requests**: Cumulative count of all LLM API requests
- **Request Rate**: Requests per second, broken down by model
- **Average Latency**: Mean response time in milliseconds

### Token Metrics
- **Token Usage Rate**: Tokens consumed per second (input vs output)
- **Token Distribution**: Percentile analysis (p50, p95, p99) of token usage
- **Time Per Output Token**: How fast the model generates tokens

### Cost Metrics
- **Cost Rate ($/sec)**: Real-time cost estimation based on current token usage
- **Estimated Total Cost**: Cumulative cost over selected time range
- Costs are approximate and based on standard pricing for each provider

## Cost Pricing Reference

| Provider | Input (per 1M tokens) | Output (per 1M tokens) |
|----------|----------------------|------------------------|
| **Anthropic Claude Haiku** | $3.00 | $15.00 |
| **OpenAI GPT-4o-mini** | $0.15 | $0.60 |
| **xAI Grok** | $2.00 | $10.00 |
| **Google Gemini 1.5 Flash** | $0.075 | $0.30 |

> **Note**: Actual pricing may vary. Update the multipliers in dashboard JSON files if needed.

## Customizing Dashboards

### Updating Cost Calculations

To update pricing for a provider, edit the dashboard JSON file and modify the multipliers:

```json
// For input tokens
"expr": "sum(rate(...{gen_ai_token_type=\"input\"}[...])) * 0.000003"
//                                                              ^^^^^^^^
//                                                         Cost per token

// For output tokens
"expr": "sum(rate(...{gen_ai_token_type=\"output\"}[...])) * 0.000015"
```

**Formula**: `(Price per 1M tokens) / 1,000,000 = multiplier`

Examples:
- $3/M tokens = 0.000003
- $0.15/M tokens = 0.00000015

### Adding New Providers

1. Create a new route in `agentgateway.yaml` with a unique path prefix
2. Copy an existing dashboard JSON file
3. Update the route filter regex (e.g., `route=~".*newprovider.*"`)
4. Update titles and labels
5. Update cost multipliers based on provider pricing
6. Save to `monitoring/grafana/dashboards/`

### Prometheus Configuration

Edit `monitoring/prometheus/prometheus.yml` to adjust:
- Scrape interval (default: 15s)
- Scrape timeout
- Additional targets

## Troubleshooting

### No data in Grafana

1. Check if Prometheus is scraping metrics:
   - Visit http://localhost:9090/targets
   - Verify "agentgateway" target is UP

2. Check AgentGateway metrics endpoint:
   - Visit http://localhost:15020/metrics
   - Verify metrics like `agentgateway_gen_ai_server_request_duration_count` exist

3. Test a query in Prometheus:
   - Visit http://localhost:9090/graph
   - Query: `agentgateway_gen_ai_server_request_duration_count`

### Dashboards not loading

1. Check Grafana logs:
```bash
docker-compose logs grafana
```

2. Verify provisioning directories are mounted:
```bash
docker-compose exec grafana ls -la /etc/grafana/provisioning/dashboards
docker-compose exec grafana ls -la /var/lib/grafana/dashboards
```

3. Manually import dashboard:
   - Go to Grafana → Dashboards → New → Import
   - Upload the JSON file

### Cost estimates seem wrong

1. Verify the pricing multipliers in the dashboard match current pricing
2. Check if the route filter regex matches your AgentGateway configuration
3. Ensure token usage metrics are being reported correctly

## Directory Structure

```
monitoring/
├── README.md                           # This file
├── prometheus/
│   └── prometheus.yml                  # Prometheus configuration
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── prometheus.yml          # Grafana datasource config
    │   └── dashboards/
    │       └── dashboards.yml          # Dashboard provisioning config
    └── dashboards/
        ├── global-cost-dashboard.json  # Global overview
        ├── anthropic-dashboard.json    # Anthropic-specific
        ├── openai-dashboard.json       # OpenAI-specific
        ├── xai-dashboard.json          # xAI-specific
        └── gemini-dashboard.json       # Gemini-specific
```

## Data Retention

- **Prometheus**: Default 15 days (configurable in prometheus.yml)
- **Grafana**: Persistent storage via Docker volumes

To adjust Prometheus retention:
```yaml
command:
  - '--storage.tsdb.retention.time=30d'  # Keep 30 days
```

## Best Practices

1. **Set up alerts**: Configure Grafana alerts for cost thresholds
2. **Regular review**: Check the Global Cost Dashboard daily/weekly
3. **Budget tracking**: Use sum calculations to track total spend over time periods
4. **Performance monitoring**: Watch p95/p99 latency metrics for SLA compliance
5. **Cost optimization**: Compare providers using the global dashboard to find best value

## Integration with Tracing

This setup works alongside Jaeger tracing. For complete observability:
- **Jaeger**: http://localhost:16686 (distributed tracing)
- **Prometheus/Grafana**: Metrics and dashboards (this setup)
- **AgentGateway Admin**: http://localhost:15000 (live configuration)

## Support

For issues or questions:
- AgentGateway docs: [Link to docs]
- Prometheus docs: https://prometheus.io/docs/
- Grafana docs: https://grafana.com/docs/
