/**
 * Simple A2A Hello Agent
 *
 * This agent demonstrates the A2A protocol by providing greeting capabilities.
 * It exposes an agent card at /.well-known/agent.json and handles task requests.
 */

const express = require('express');
const app = express();
const PORT = 9001;

app.use(express.json());

// Agent Card - Describes the agent's capabilities
const agentCard = {
  "name": "Hello Agent",
  "version": "1.0.0",
  "url": "http://localhost:3000",
  "description": "A simple greeting agent that can say hello in multiple languages",
  "capabilities": {
    "streaming": false,
    "interactive": true
  },
  "skills": [
    {
      "name": "greet",
      "description": "Greet someone with a personalized message",
      "parameters": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "The name of the person to greet"
          },
          "language": {
            "type": "string",
            "description": "Language for greeting (english, spanish, french)",
            "enum": ["english", "spanish", "french"],
            "default": "english"
          }
        },
        "required": ["name"]
      }
    },
    {
      "name": "introduce",
      "description": "Get a self-introduction from the agent",
      "parameters": {
        "type": "object",
        "properties": {}
      }
    }
  ]
};

// Agent Card Endpoint - Required by A2A protocol
// Handle both root path and prefixed path
app.get('/.well-known/agent.json', (req, res) => {
  console.log('Agent card requested');
  res.json(agentCard);
});

app.get('/agent/hello/.well-known/agent.json', (req, res) => {
  console.log('Agent card requested (with prefix)');
  res.json(agentCard);
});

// Shared task handling logic
function handleTask(req, res) {
  const { skill, parameters } = req.body;

  console.log(`Task requested: ${skill}`, parameters);

  try {
    let result;

    if (skill === 'greet') {
      const { name, language = 'english' } = parameters;
      const greetings = {
        english: `Hello, ${name}! Welcome to the A2A demo!`,
        spanish: `¡Hola, ${name}! ¡Bienvenido a la demostración A2A!`,
        french: `Bonjour, ${name}! Bienvenue dans la démo A2A!`
      };

      result = {
        success: true,
        output: {
          type: "text",
          text: greetings[language] || greetings.english
        }
      };
    } else if (skill === 'introduce') {
      result = {
        success: true,
        output: {
          type: "text",
          text: "I am the Hello Agent! I can greet people in multiple languages. Try asking me to greet someone!"
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
app.post('/agent/hello/task', handleTask);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', agent: 'hello-agent' });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Hello Agent is running',
    endpoints: {
      agentCard: '/.well-known/agent.json',
      task: '/task',
      health: '/health'
    }
  });
});

app.listen(PORT, () => {
  console.log(`Hello Agent listening on port ${PORT}`);
  console.log(`Agent card available at: http://localhost:${PORT}/.well-known/agent.json`);
  console.log(`Access via AgentGateway at: http://localhost:3000/agent/hello`);
});
