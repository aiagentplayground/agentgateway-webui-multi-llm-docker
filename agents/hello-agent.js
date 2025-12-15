/**
 * Hello Agent - Refactored with MCP Integration
 */
const A2AAgentBase = require('./lib/a2a-agent-base');

// Define native skill schemas
const nativeSkills = [
  {
    name: 'greet',
    description: 'Greet someone with a personalized message',
    parameters: {
      type: 'object',
      properties: {
        name: {
          type: 'string',
          description: 'The name of the person to greet'
        },
        language: {
          type: 'string',
          description: 'Language for greeting (english, spanish, french)',
          enum: ['english', 'spanish', 'french'],
          default: 'english'
        }
      },
      required: ['name']
    }
  },
  {
    name: 'introduce',
    description: 'Get a self-introduction from the agent',
    parameters: {
      type: 'object',
      properties: {}
    }
  }
];

// Define native skill handlers
const skillHandlers = {
  greet: async (parameters) => {
    const { name, language = 'english' } = parameters;
    const greetings = {
      english: `Hello, ${name}! Welcome to the A2A demo with MCP integration!`,
      spanish: `¡Hola, ${name}! ¡Bienvenido a la demostración A2A con integración MCP!`,
      french: `Bonjour, ${name}! Bienvenue dans la démo A2A avec intégration MCP!`
    };

    return {
      success: true,
      output: {
        type: 'text',
        text: greetings[language] || greetings.english
      }
    };
  },

  introduce: async (parameters) => {
    return {
      success: true,
      output: {
        type: 'text',
        text: 'I am the Hello Agent! I can greet people in multiple languages and also use MCP tools for additional capabilities!'
      }
    };
  }
};

// Create and start the agent
const agent = new A2AAgentBase({
  name: 'Hello Agent',
  version: '1.0.0',
  description: 'A simple greeting agent with MCP tool integration',
  port: 9001,
  url: 'http://localhost:3000/agent/hello',
  skills: nativeSkills,
  skillHandlers: skillHandlers,
  mcp: {
    enabled: true,
    endpoint: process.env.MCP_ENDPOINT || 'http://agentgateway:3000/mcp/stdio'
  }
});

// Override route prefix
agent.getRoutePrefix = () => '/agent/hello';

// Start the agent
agent.start().catch(error => {
  console.error('Failed to start Hello Agent:', error);
  process.exit(1);
});
