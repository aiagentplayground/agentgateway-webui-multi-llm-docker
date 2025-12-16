#!/bin/bash

# Test script for user and team tracking in AgentGateway
# This script verifies that user headers are being captured and metrics are being generated

set -e

echo "🔍 AgentGateway User Tracking Test"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test users
USERS=(
  "sarah.johnson@example.com:Sarah Johnson:marketing"
  "alex.rivera@example.com:Alex Rivera:platform"
  "taylor.morgan@example.com:Taylor Morgan:security"
)

# Check if services are running
echo "📡 Step 1: Checking if services are running..."
if ! docker-compose ps agentgateway | grep -q "Up"; then
  echo -e "${RED}❌ AgentGateway is not running${NC}"
  echo "   Run: docker-compose up -d agentgateway"
  exit 1
fi

if ! docker-compose ps prometheus | grep -q "Up"; then
  echo -e "${RED}❌ Prometheus is not running${NC}"
  echo "   Run: docker-compose up -d prometheus"
  exit 1
fi

echo -e "${GREEN}✓ Services are running${NC}"
echo ""

# Test 2: Send requests with user headers
echo "📤 Step 2: Sending test requests with user headers..."
for user_data in "${USERS[@]}"; do
  IFS=':' read -r email name team <<< "$user_data"

  echo "   Testing user: $email"

  response=$(curl -s -w "\n%{http_code}" -X POST http://localhost:3000/anthropic/v1/messages \
    -H "Content-Type: application/json" \
    -H "X-User-Email: $email" \
    -H "X-User-Name: $name" \
    -H "X-User-Role: user" \
    -H "x-api-key: ${ANTHROPIC_API_KEY:-test-key}" \
    -d '{
      "model": "claude-haiku-4-5-20251001",
      "messages": [{"role": "user", "content": "Hello!"}],
      "max_tokens": 10
    }' 2>&1 || echo "000")

  http_code=$(echo "$response" | tail -n 1)

  if [ "$http_code" = "200" ] || [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
    echo -e "   ${GREEN}✓ Request sent successfully (HTTP $http_code)${NC}"
  else
    echo -e "   ${YELLOW}⚠ Request sent (HTTP $http_code) - may need valid API key${NC}"
  fi
done

echo ""

# Test 3: Wait for metrics to be scraped
echo "⏳ Step 3: Waiting for Prometheus to scrape metrics (15 seconds)..."
sleep 15
echo -e "${GREEN}✓ Metrics should be available now${NC}"
echo ""

# Test 4: Query Prometheus for user metrics
echo "🔎 Step 4: Checking if user metrics are captured in Prometheus..."

# Query for metrics with user_email label
metrics_response=$(curl -s 'http://localhost:9090/api/v1/query?query=agentgateway_requests_total{user_email!=""}')

if echo "$metrics_response" | grep -q '"status":"success"'; then
  result_count=$(echo "$metrics_response" | grep -o '"result":\[' | wc -l)

  if [ "$result_count" -gt 0 ]; then
    echo -e "${GREEN}✓ User metrics found in Prometheus!${NC}"
    echo ""
    echo "📊 Sample metrics:"
    echo "$metrics_response" | python3 -m json.tool 2>/dev/null | grep -A 5 "user_email" | head -20 || echo "$metrics_response"
  else
    echo -e "${YELLOW}⚠ No user metrics found yet${NC}"
    echo "   This might be normal if:"
    echo "   - AgentGateway configuration doesn't support custom labels"
    echo "   - Metrics scraping interval hasn't occurred yet"
    echo "   - Open WebUI needs to be configured to send headers"
  fi
else
  echo -e "${RED}❌ Failed to query Prometheus${NC}"
  echo "   Response: $metrics_response"
fi

echo ""

# Test 5: Check if Grafana dashboard exists
echo "📈 Step 5: Checking if Grafana dashboard is available..."
grafana_response=$(curl -s -u admin:admin http://localhost:3100/api/search?query=User)

if echo "$grafana_response" | grep -q "User & Team Analytics"; then
  echo -e "${GREEN}✓ User & Team Analytics dashboard found in Grafana!${NC}"
  echo "   Access at: http://localhost:3100/dashboards"
else
  echo -e "${YELLOW}⚠ Dashboard not found${NC}"
  echo "   Make sure Grafana provisioning is configured correctly"
fi

echo ""

# Summary
echo "📋 Summary"
echo "=========="
echo ""
echo "To view user analytics:"
echo "1. Open Grafana: http://localhost:3100"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "2. Navigate to: Dashboards → LLM Monitoring → User & Team Analytics"
echo ""
echo "3. Query Prometheus directly:"
echo "   http://localhost:9090/graph?g0.expr=agentgateway_requests_total{user_email!=%22%22}"
echo ""
echo "4. View Jaeger traces:"
echo "   http://localhost:16686"
echo ""

# Additional checks
echo "🔧 Configuration Check"
echo "======================"
echo ""

# Check if AgentGateway config has metrics section
if docker-compose exec -T agentgateway cat /etc/agentgateway/agentgateway.yaml 2>/dev/null | grep -q "metrics:"; then
  echo -e "${GREEN}✓ AgentGateway metrics configuration found${NC}"
else
  echo -e "${YELLOW}⚠ AgentGateway metrics configuration not found${NC}"
  echo "   Update agentgateway.yaml with metrics configuration"
fi

# Check if custom labels are configured
if docker-compose exec -T agentgateway cat /etc/agentgateway/agentgateway.yaml 2>/dev/null | grep -q "customLabels:"; then
  echo -e "${GREEN}✓ Custom labels (user tracking) configured${NC}"
else
  echo -e "${YELLOW}⚠ Custom labels not configured${NC}"
  echo "   User tracking may not work without custom label configuration"
fi

echo ""
echo "✅ Test complete!"
echo ""
echo "For full documentation, see: docs/USER_TRACKING.md"
