# MCP Server Examples and Testing Guide

This guide provides complete examples for testing MCP server connections through AgentGateway.

## Prerequisites

- AgentGateway running on port 3000
- Node.js installed (for stdio examples)
- curl or similar HTTP client

## Testing the Stdio Connection

The stdio connection uses the `@modelcontextprotocol/server-everything` package, which provides a comprehensive set of demo tools.

### 1. List Available Tools

```bash
curl -X POST http://localhost:3000/mcp/stdio \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

Expected response includes a list of available tools like `echo`, `add`, `longRunningOperation`, etc.

### 2. Call the Echo Tool

```bash
curl -X POST http://localhost:3000/mcp/stdio \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "echo",
      "arguments": {
        "message": "Hello from AgentGateway MCP!"
      }
    }
  }'
```

### 3. Get Server Info

```bash
curl -X POST http://localhost:3000/mcp/stdio \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "agentgateway-test",
        "version": "1.0.0"
      }
    }
  }'
```

## Testing the HTTP Connection

The HTTP connection requires an MCP server running on HTTP. Here's how to set up and test it.

### Setting Up a Simple MCP HTTP Server

Create a file `simple-mcp-server.js`:

```javascript
const express = require('express');
const app = express();
app.use(express.json());

// MCP server endpoint
app.post('/mcp/', (req, res) => {
  const { method, params, id } = req.body;

  if (method === 'initialize') {
    res.json({
      jsonrpc: '2.0',
      id: id,
      result: {
        protocolVersion: '2024-11-05',
        serverInfo: {
          name: 'simple-mcp-server',
          version: '1.0.0'
        },
        capabilities: {
          tools: {}
        }
      }
    });
  } else if (method === 'tools/list') {
    res.json({
      jsonrpc: '2.0',
      id: id,
      result: {
        tools: [
          {
            name: 'hello',
            description: 'Says hello',
            inputSchema: {
              type: 'object',
              properties: {
                name: {
                  type: 'string',
                  description: 'Name to greet'
                }
              },
              required: ['name']
            }
          }
        ]
      }
    });
  } else if (method === 'tools/call') {
    const { name, arguments: args } = params;
    if (name === 'hello') {
      res.json({
        jsonrpc: '2.0',
        id: id,
        result: {
          content: [
            {
              type: 'text',
              text: `Hello, ${args.name}!`
            }
          ]
        }
      });
    }
  } else {
    res.status(400).json({
      jsonrpc: '2.0',
      id: id,
      error: {
        code: -32601,
        message: 'Method not found'
      }
    });
  }
});

app.listen(3005, () => {
  console.log('MCP server running on http://localhost:3005');
});
```

### Start the HTTP MCP Server

```bash
npm install express
node simple-mcp-server.js
```

### Test the HTTP Connection

Once your MCP server is running on port 3005:

```bash
# List tools from HTTP MCP server
curl -X POST http://localhost:3000/mcp/http \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Call the hello tool
curl -X POST http://localhost:3000/mcp/http \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "hello",
      "arguments": {
        "name": "AgentGateway"
      }
    }
  }'
```

## Using the AgentGateway UI

The AgentGateway UI provides an interactive way to explore and test MCP servers.

1. Open http://localhost:15000/ui/ in your browser
2. Navigate to the MCP section
3. Select either the stdio or HTTP backend
4. Browse available tools
5. Execute tools with custom parameters
6. View responses in real-time

## Common MCP Methods

### Initialize

Establishes a connection and exchanges capabilities:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "client-name",
      "version": "1.0.0"
    }
  }
}
```

### List Tools

Retrieves all available tools from the MCP server:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

### Call Tool

Executes a specific tool with arguments:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "tool-name",
    "arguments": {
      "param1": "value1",
      "param2": "value2"
    }
  }
}
```

### List Resources

Lists available resources (if supported):

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "resources/list"
}
```

### List Prompts

Lists available prompts (if supported):

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "prompts/list"
}
```

## Advanced Configuration

### Multiple MCP Servers

You can configure multiple MCP servers by adding more targets:

```yaml
backends:
  - name: mcp-stdio-backend
    target:
      mcp:
        targets:
          - name: everything
            stdio:
              cmd: npx
              args:
                - "-y"
                - "@modelcontextprotocol/server-everything"
          - name: custom-tools
            stdio:
              cmd: node
              args:
                - "./my-custom-mcp-server.js"
```

### Environment Variables for Stdio

Pass environment variables to stdio MCP servers:

```yaml
- name: mcp-with-env
  stdio:
    cmd: node
    args:
      - "./mcp-server.js"
    env:
      API_KEY: "${MY_API_KEY}"
      DEBUG: "true"
```

### HTTP with Authentication

Configure HTTP MCP servers with authentication headers:

```yaml
- name: mcp-http-auth
  http:
    host: http://localhost:3005/mcp/
    headers:
      Authorization: "Bearer ${MCP_TOKEN}"
```

## Troubleshooting

### Stdio Connection Issues

1. **Server not starting**: Check that the command and args are correct
2. **Tool execution fails**: Verify the tool name and arguments match the server's schema
3. **Timeout errors**: Some tools may take longer to execute; consider increasing timeout settings

### HTTP Connection Issues

1. **Connection refused**: Ensure your MCP server is running and accessible
2. **404 errors**: Verify the HTTP path matches your server's endpoint
3. **CORS errors**: The gateway handles CORS, but your MCP server should accept requests from the gateway

### General Debugging

Enable detailed logging in AgentGateway:

```bash
docker-compose logs -f agentgateway
```

Look for MCP-related messages showing connection attempts, tool calls, and responses.

## Best Practices

1. **Use Stdio for Development**: Easier to set up and test
2. **Use HTTP for Production**: Better scalability and reliability
3. **Implement Health Checks**: Add health check endpoints to your HTTP MCP servers
4. **Version Your Tools**: Include version information in tool schemas
5. **Document Tool Schemas**: Provide clear descriptions and examples for each tool
6. **Handle Errors Gracefully**: Return proper JSON-RPC error responses
7. **Test Tool Schemas**: Validate that your input schemas match actual tool requirements

## Observability and Monitoring

### Accessing Metrics

View Prometheus-compatible metrics for MCP tool usage:

```bash
# Get all metrics
curl http://localhost:15020/metrics

# Filter for MCP-specific metrics
curl http://localhost:15020/metrics | grep list_calls

# Watch metrics in real-time
watch -n 1 'curl -s http://localhost:15020/metrics | grep list_calls_total'
```

**Example Metrics Output:**
```
# HELP list_calls_total Total number of tool calls
# TYPE list_calls_total counter
list_calls_total{server="everything",tool="echo"} 15
list_calls_total{server="everything",tool="add"} 8
list_calls_total{server="everything",tool="longRunningOperation"} 3
```

### Using Jaeger for Distributed Tracing

1. **Access Jaeger UI**: Open http://localhost:16686 in your browser

2. **View MCP Traces**:
   - Select "agentgateway" from the Service dropdown
   - Choose operation type (e.g., "call_tool", "tools/list")
   - Click "Find Traces"

3. **Analyze a Trace**:
   - Click on a trace to view details
   - See timing breakdown for each operation
   - View request/response payloads
   - Identify bottlenecks and errors

4. **Filter Traces**:
   ```
   # Search by operation
   operation="call_tool"

   # Search by tags
   mcp.server="everything"
   mcp.tool="echo"

   # Search by duration
   minDuration=100ms
   ```

### Example: End-to-End Observability Workflow

**Step 1: Make an MCP request**
```bash
curl -X POST http://localhost:3000/mcp/stdio \
  -H "Content-Type: application/json" \
  -H "mcp-protocol-version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "echo",
      "arguments": {"message": "test"}
    }
  }'
```

**Step 2: Check metrics**
```bash
curl -s http://localhost:15020/metrics | grep 'list_calls_total.*echo'
```

**Step 3: View trace in Jaeger**
- Open http://localhost:16686
- Search for recent "call_tool" operations
- Find your echo request and inspect timing

**Step 4: Review logs**
```bash
docker-compose logs --tail=50 agentgateway | grep echo
```

### Monitoring Production MCP Servers

For production deployments, consider:

1. **Metrics Scraping**: Configure Prometheus to scrape metrics
   ```yaml
   scrape_configs:
     - job_name: 'agentgateway'
       static_configs:
         - targets: ['localhost:15020']
   ```

2. **Alerting Rules**: Set up alerts for critical metrics
   ```yaml
   groups:
     - name: mcp_alerts
       rules:
         - alert: HighErrorRate
           expr: rate(list_calls_total{status="error"}[5m]) > 0.1
           annotations:
             summary: "High error rate on MCP tool calls"
   ```

3. **Dashboard Creation**: Build Grafana dashboards
   - Tool usage by server and tool name
   - Request latency percentiles
   - Error rates and types
   - Active connections

4. **Trace Sampling**: Adjust sampling rate for production
   ```yaml
   telemetry:
     otlpEndpoint: http://jaeger:4317
     randomSampling: false  # Use head-based sampling
     samplingRate: 0.1      # Sample 10% of requests
   ```

### Debugging with Observability

**Scenario: Tool calls are slow**

1. Check metrics for latency:
   ```bash
   curl -s http://localhost:15020/metrics | grep duration
   ```

2. Find slow traces in Jaeger:
   - Filter by `minDuration=1s`
   - Identify which span is taking the longest

3. Review logs for errors:
   ```bash
   docker-compose logs agentgateway | grep -i error
   ```

**Scenario: Some tools aren't being called**

1. Check tool call distribution:
   ```bash
   curl -s http://localhost:15020/metrics | grep list_calls_total
   ```

2. Verify tool is listed:
   ```bash
   curl -X POST http://localhost:3000/mcp/stdio \
     -H "Content-Type: application/json" \
     -H "mcp-protocol-version: 2024-11-05" \
     -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
   ```

3. Review initialization traces in Jaeger

## Additional Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [AgentGateway MCP Documentation](https://agentgateway.dev/docs/mcp/)
- [MCP Observability Guide](https://agentgateway.dev/docs/mcp/mcp-observability/)
- [MCP Server Examples](https://github.com/modelcontextprotocol)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry](https://opentelemetry.io/)
