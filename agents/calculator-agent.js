/**
 * Simple A2A Calculator Agent
 *
 * This agent demonstrates the A2A protocol by providing calculation capabilities.
 * It exposes an agent card at /.well-known/agent.json and handles task requests.
 */

const express = require('express');
const app = express();
const PORT = 9002;

app.use(express.json());

// Agent Card - Describes the agent's capabilities
const agentCard = {
  "name": "Calculator Agent",
  "version": "1.0.0",
  "url": "http://localhost:3000/agent/calculator",
  "description": "A mathematical calculation agent that can perform basic arithmetic operations",
  "capabilities": {
    "streaming": false,
    "interactive": true
  },
  "skills": [
    {
      "name": "calculate",
      "description": "Perform a mathematical calculation",
      "parameters": {
        "type": "object",
        "properties": {
          "operation": {
            "type": "string",
            "description": "The operation to perform",
            "enum": ["add", "subtract", "multiply", "divide"],
          },
          "a": {
            "type": "number",
            "description": "First number"
          },
          "b": {
            "type": "number",
            "description": "Second number"
          }
        },
        "required": ["operation", "a", "b"]
      }
    },
    {
      "name": "power",
      "description": "Calculate a number raised to a power",
      "parameters": {
        "type": "object",
        "properties": {
          "base": {
            "type": "number",
            "description": "Base number"
          },
          "exponent": {
            "type": "number",
            "description": "Exponent"
          }
        },
        "required": ["base", "exponent"]
      }
    },
    {
      "name": "sqrt",
      "description": "Calculate the square root of a number",
      "parameters": {
        "type": "object",
        "properties": {
          "number": {
            "type": "number",
            "description": "Number to calculate square root of"
          }
        },
        "required": ["number"]
      }
    }
  ]
};

// Agent Card Endpoint - Required by A2A protocol
app.get('/.well-known/agent.json', (req, res) => {
  console.log('Agent card requested');
  res.json(agentCard);
});

app.get('/agent/calculator/.well-known/agent.json', (req, res) => {
  console.log('Agent card requested (with prefix)');
  res.json(agentCard);
});

// Shared task handling logic
function handleTask(req, res) {
  const { skill, parameters } = req.body;

  console.log(`Task requested: ${skill}`, parameters);

  try {
    let result;

    if (skill === 'calculate') {
      const { operation, a, b } = parameters;
      let answer;

      switch (operation) {
        case 'add':
          answer = a + b;
          break;
        case 'subtract':
          answer = a - b;
          break;
        case 'multiply':
          answer = a * b;
          break;
        case 'divide':
          if (b === 0) {
            return res.json({
              success: false,
              error: {
                code: "DIVISION_BY_ZERO",
                message: "Cannot divide by zero"
              }
            });
          }
          answer = a / b;
          break;
        default:
          return res.json({
            success: false,
            error: {
              code: "INVALID_OPERATION",
              message: `Invalid operation: ${operation}`
            }
          });
      }

      result = {
        success: true,
        output: {
          type: "text",
          text: `${a} ${operation} ${b} = ${answer}`,
          data: {
            operation,
            operands: [a, b],
            result: answer
          }
        }
      };
    } else if (skill === 'power') {
      const { base, exponent } = parameters;
      const answer = Math.pow(base, exponent);

      result = {
        success: true,
        output: {
          type: "text",
          text: `${base} ^ ${exponent} = ${answer}`,
          data: {
            base,
            exponent,
            result: answer
          }
        }
      };
    } else if (skill === 'sqrt') {
      const { number } = parameters;

      if (number < 0) {
        return res.json({
          success: false,
          error: {
            code: "INVALID_INPUT",
            message: "Cannot calculate square root of negative number"
          }
        });
      }

      const answer = Math.sqrt(number);

      result = {
        success: true,
        output: {
          type: "text",
          text: `√${number} = ${answer}`,
          data: {
            input: number,
            result: answer
          }
        }
      };
    } else {
      result = {
        success: false,
        error: {
          code: "UNKNOWN_SKILL",
          message: `Unknown skill: ${skill}`
        }
      };
    }

    res.json(result);
  } catch (error) {
    console.error('Error processing task:', error);
    res.status(500).json({
      success: false,
      error: {
        code: "INTERNAL_ERROR",
        message: error.message
      }
    });
  }
}

// Task Endpoint - both root and prefixed paths
app.post('/task', handleTask);
app.post('/agent/calculator/task', handleTask);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', agent: 'calculator-agent' });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Calculator Agent is running',
    endpoints: {
      agentCard: '/.well-known/agent.json',
      task: '/task',
      health: '/health'
    }
  });
});

app.listen(PORT, () => {
  console.log(`Calculator Agent listening on port ${PORT}`);
  console.log(`Agent card available at: http://localhost:${PORT}/.well-known/agent.json`);
  console.log(`Access via AgentGateway at: http://localhost:3000/agent/calculator`);
});
