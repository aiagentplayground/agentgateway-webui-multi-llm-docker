/**
 * Calculator Agent - Refactored with MCP Integration
 */
const A2AAgentBase = require('./lib/a2a-agent-base');

// Define native skill schemas
const nativeSkills = [
  {
    name: 'calculate',
    description: 'Perform a mathematical calculation',
    parameters: {
      type: 'object',
      properties: {
        operation: {
          type: 'string',
          description: 'The operation to perform',
          enum: ['add', 'subtract', 'multiply', 'divide']
        },
        a: {
          type: 'number',
          description: 'First number'
        },
        b: {
          type: 'number',
          description: 'Second number'
        }
      },
      required: ['operation', 'a', 'b']
    }
  },
  {
    name: 'power',
    description: 'Calculate a number raised to a power',
    parameters: {
      type: 'object',
      properties: {
        base: {
          type: 'number',
          description: 'Base number'
        },
        exponent: {
          type: 'number',
          description: 'Exponent'
        }
      },
      required: ['base', 'exponent']
    }
  },
  {
    name: 'sqrt',
    description: 'Calculate the square root of a number',
    parameters: {
      type: 'object',
      properties: {
        number: {
          type: 'number',
          description: 'Number to calculate square root of'
        }
      },
      required: ['number']
    }
  }
];

// Define native skill handlers
const skillHandlers = {
  calculate: async (parameters) => {
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
          return {
            success: false,
            error: {
              code: 'DIVISION_BY_ZERO',
              message: 'Cannot divide by zero'
            }
          };
        }
        answer = a / b;
        break;
      default:
        return {
          success: false,
          error: {
            code: 'INVALID_OPERATION',
            message: `Invalid operation: ${operation}`
          }
        };
    }

    return {
      success: true,
      output: {
        type: 'text',
        text: `${a} ${operation} ${b} = ${answer}`,
        data: {
          operation,
          operands: [a, b],
          result: answer
        }
      }
    };
  },

  power: async (parameters) => {
    const { base, exponent } = parameters;
    const answer = Math.pow(base, exponent);

    return {
      success: true,
      output: {
        type: 'text',
        text: `${base} ^ ${exponent} = ${answer}`,
        data: {
          base,
          exponent,
          result: answer
        }
      }
    };
  },

  sqrt: async (parameters) => {
    const { number } = parameters;

    if (number < 0) {
      return {
        success: false,
        error: {
          code: 'INVALID_INPUT',
          message: 'Cannot calculate square root of negative number'
        }
      };
    }

    const answer = Math.sqrt(number);

    return {
      success: true,
      output: {
        type: 'text',
        text: `√${number} = ${answer}`,
        data: {
          input: number,
          result: answer
        }
      }
    };
  }
};

// Create and start the agent
const agent = new A2AAgentBase({
  name: 'Calculator Agent',
  version: '1.0.0',
  description: 'A mathematical calculation agent with MCP tool integration',
  port: 9002,
  url: 'http://localhost:3000/agent/calculator',
  skills: nativeSkills,
  skillHandlers: skillHandlers,
  mcp: {
    enabled: true,
    endpoint: process.env.MCP_ENDPOINT || 'http://agentgateway:3000/mcp/stdio'
  }
});

// Override route prefix
agent.getRoutePrefix = () => '/agent/calculator';

// Start the agent
agent.start().catch(error => {
  console.error('Failed to start Calculator Agent:', error);
  process.exit(1);
});
