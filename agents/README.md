# A2A Demo Agents

This directory contains example agents that demonstrate the Agent-to-Agent (A2A) protocol with AgentGateway.

## What is A2A?

A2A (Agent-to-Agent) is an open protocol developed by Google that enables communication and interoperability between agentic applications. It allows agents to:

- Discover capabilities of other agents
- Negotiate interaction methods
- Collaborate securely on tasks
- Operate independently without exposing internal systems

## Available Agents

### 1. Hello Agent (Port 9001)

A simple greeting agent that demonstrates basic A2A capabilities.

**Skills:**
- `greet`: Greet someone with a personalized message in multiple languages
- `introduce`: Get a self-introduction from the agent

**Endpoint:** http://localhost:3000/agent/hello

### 2. Calculator Agent (Port 9002)

A mathematical calculation agent that performs arithmetic operations.

**Skills:**
- `calculate`: Perform basic arithmetic (add, subtract, multiply, divide)
- `power`: Calculate a number raised to a power
- `sqrt`: Calculate the square root of a number

**Endpoint:** http://localhost:3000/agent/calculator

## Quick Start

### Option 1: Docker (Recommended)

The agents run automatically with the main docker-compose setup:

```bash
# From the project root
docker-compose up -d --build
```

This starts both agents as Docker containers along with AgentGateway and other services.

### Option 2: Manual Node.js (Development)

If you want to run agents manually for development:

**Install Dependencies:**
```bash
cd agents
npm install
```

**Run Individual Agents:**
```bash
npm run hello      # Hello Agent on port 9001
npm run calculator # Calculator Agent on port 9002
```

**Run All Agents:**
```bash
npm run start-all
```

**Note:** When running manually, update `agentgateway.yaml` to use `localhost` instead of container names:
```yaml
host: localhost:9001  # instead of hello-agent:9001
```

## Testing the Agents

### 1. Check Agent Card

Each agent exposes its capabilities via an agent card:

```bash
# Hello Agent card
curl http://localhost:3000/agent/hello/.well-known/agent.json

# Calculator Agent card
curl http://localhost:3000/agent/calculator/.well-known/agent.json
```

### 2. Execute Tasks

**Hello Agent - Greet in English:**
```bash
curl -X POST http://localhost:3000/agent/hello/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "greet",
    "parameters": {
      "name": "Alice",
      "language": "english"
    }
  }'
```

**Hello Agent - Greet in Spanish:**
```bash
curl -X POST http://localhost:3000/agent/hello/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "greet",
    "parameters": {
      "name": "Carlos",
      "language": "spanish"
    }
  }'
```

**Hello Agent - Introduction:**
```bash
curl -X POST http://localhost:3000/agent/hello/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "introduce",
    "parameters": {}
  }'
```

**Calculator Agent - Addition:**
```bash
curl -X POST http://localhost:3000/agent/calculator/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "calculate",
    "parameters": {
      "operation": "add",
      "a": 15,
      "b": 27
    }
  }'
```

**Calculator Agent - Power:**
```bash
curl -X POST http://localhost:3000/agent/calculator/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "power",
    "parameters": {
      "base": 2,
      "exponent": 10
    }
  }'
```

**Calculator Agent - Square Root:**
```bash
curl -X POST http://localhost:3000/agent/calculator/task \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "sqrt",
    "parameters": {
      "number": 144
    }
  }'
```

## A2A Protocol Structure

### Agent Card (/.well-known/agent.json)

The agent card describes the agent's capabilities and available skills:

```json
{
  "name": "Agent Name",
  "version": "1.0.0",
  "description": "Agent description",
  "capabilities": {
    "streaming": false,
    "interactive": true
  },
  "skills": [
    {
      "name": "skill-name",
      "description": "What the skill does",
      "parameters": {
        "type": "object",
        "properties": {
          "param1": {
            "type": "string",
            "description": "Parameter description"
          }
        },
        "required": ["param1"]
      }
    }
  ]
}
```

### Task Request Format

```json
{
  "skill": "skill-name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Task Response Format

**Success:**
```json
{
  "success": true,
  "output": {
    "type": "text",
    "text": "Result text",
    "data": {
      "key": "value"
    }
  }
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## Accessing via AgentGateway UI

1. Ensure AgentGateway and agents are running
2. Open http://localhost:15000 in your browser
3. Navigate to the A2A section
4. Discover and interact with agents through the UI

## Creating Your Own A2A Agent

To create a custom A2A agent:

1. **Implement Required Endpoints:**
   - `GET /.well-known/agent.json` - Agent card
   - `POST /task` - Task execution

2. **Define Skills:** Describe what your agent can do in the agent card

3. **Handle Task Requests:** Process incoming tasks and return structured responses

4. **Add to AgentGateway:** Update `agentgateway.yaml`:
   ```yaml
   routes:
     - name: my-agent-route
       match:
         prefix: /agent/myagent
       policies:
         - cors
         - a2a
       backends:
         - my-agent-backend

   backends:
     - name: my-agent-backend
       target:
         host: localhost:9003
   ```

5. **Restart AgentGateway:** Apply the new configuration

## Observability

A2A agent interactions are fully observable through:

- **Metrics:** http://localhost:15020/metrics
- **Traces:** http://localhost:16686 (Jaeger UI)
- **Logs:** `docker-compose logs -f agentgateway`

## Best Practices

1. **Clear Skill Descriptions:** Provide detailed descriptions for each skill
2. **Parameter Validation:** Validate all input parameters
3. **Error Handling:** Return structured error responses
4. **Health Checks:** Implement health check endpoints
5. **Logging:** Log all task requests and responses
6. **Versioning:** Include version information in the agent card
7. **Documentation:** Document expected inputs and outputs for each skill

## Troubleshooting

**Agent not responding:**
1. Check if the agent is running: `curl http://localhost:9001/health`
2. Verify AgentGateway can reach the agent
3. Check logs: `docker-compose logs agentgateway`

**Task execution fails:**
1. Verify the agent card has the skill: `curl http://localhost:3000/agent/hello/.well-known/agent.json`
2. Check parameter format matches the schema
3. Review agent logs for errors

**Port conflicts:**
- Hello Agent: Port 9001
- Calculator Agent: Port 9002
- Ensure these ports are available

## Additional Resources

- [A2A Protocol Documentation](https://agentgateway.dev/docs/agent/about/)
- [AgentGateway A2A Guide](https://agentgateway.dev/docs/agent/a2a/)
- [Google A2A Specification](https://github.com/google/a2a)
