/**
 * A2A Agent Base Class
 * Provides MCP integration and dynamic skill management
 */
const express = require('express');
const MCPClient = require('./mcp-client');
const SchemaTransformer = require('./schema-transformer');

class A2AAgentBase {
  constructor(config) {
    this.name = config.name;
    this.version = config.version || '1.0.0';
    this.description = config.description;
    this.port = config.port;
    this.url = config.url;
    this.nativeSkills = config.skills || [];
    this.skillHandlers = config.skillHandlers || {};

    // MCP configuration
    this.mcpEnabled = config.mcp?.enabled !== false; // Default to true
    this.mcpEndpoint = config.mcp?.endpoint || 'http://agentgateway:3000/mcp/stdio';
    this.mcpClient = null;
    this.mcpTools = [];
    this.allSkills = [];

    // Express app
    this.app = express();
    this.app.use(express.json());
  }

  /**
   * Initialize the agent (setup MCP, routes, etc.)
   */
  async initialize() {
    console.log(`Initializing ${this.name}...`);

    // Initialize MCP if enabled
    if (this.mcpEnabled) {
      await this.initializeMCP();
    }

    // Combine native and MCP skills
    this.allSkills = this.buildSkillsList();

    // Setup routes
    this.setupRoutes();

    console.log(`${this.name} initialized with ${this.allSkills.length} skills`);
    console.log(`  - Native skills: ${this.nativeSkills.length}`);
    console.log(`  - MCP tools: ${this.mcpTools.length}`);
  }

  /**
   * Initialize MCP client and discover tools
   */
  async initializeMCP() {
    try {
      console.log(`Connecting to MCP at ${this.mcpEndpoint}...`);

      this.mcpClient = new MCPClient({
        endpoint: this.mcpEndpoint,
        timeout: 10000,
        maxRetries: 3
      });

      await this.mcpClient.initialize({
        name: this.name,
        version: this.version
      });

      console.log('MCP connection established');

      // Discover available tools
      const mcpTools = await this.mcpClient.listTools();
      console.log(`Discovered ${mcpTools.length} MCP tools`);

      this.mcpTools = mcpTools.map(tool =>
        SchemaTransformer.mcpToolToA2ASkill(tool)
      );

    } catch (error) {
      console.error('MCP initialization failed:', error.message);
      console.error('Agent will run with native skills only');
      this.mcpEnabled = false;
      this.mcpTools = [];
    }
  }

  /**
   * Build combined skills list (native + MCP)
   */
  buildSkillsList() {
    return [...this.nativeSkills, ...this.mcpTools];
  }

  /**
   * Setup Express routes
   */
  setupRoutes() {
    // Agent card endpoints
    this.app.get('/.well-known/agent.json', (req, res) => {
      res.json(this.getAgentCard());
    });

    // Support prefixed path for AgentGateway routing
    const prefix = this.getRoutePrefix();
    if (prefix) {
      this.app.get(`${prefix}/.well-known/agent.json`, (req, res) => {
        res.json(this.getAgentCard());
      });
    }

    // Task endpoints
    this.app.post('/task', (req, res) => this.handleTask(req, res));
    if (prefix) {
      this.app.post(`${prefix}/task`, (req, res) => this.handleTask(req, res));
    }

    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'ok',
        agent: this.name,
        mcpEnabled: this.mcpEnabled,
        mcpConnected: this.mcpClient !== null,
        skillCount: this.allSkills.length
      });
    });

    // Root endpoint
    this.app.get('/', (req, res) => {
      res.json({
        message: `${this.name} is running`,
        version: this.version,
        endpoints: {
          agentCard: '/.well-known/agent.json',
          task: '/task',
          health: '/health'
        },
        skills: this.allSkills.map(s => s.name)
      });
    });
  }

  /**
   * Get agent card with dynamic skills
   */
  getAgentCard() {
    return {
      name: this.name,
      version: this.version,
      url: this.url,
      description: this.description,
      capabilities: {
        streaming: false,
        interactive: true,
        mcpEnabled: this.mcpEnabled
      },
      skills: this.allSkills.map(skill => ({
        name: skill.name,
        description: skill.description,
        parameters: skill.parameters
      }))
    };
  }

  /**
   * Handle incoming task requests
   */
  async handleTask(req, res) {
    const { skill, parameters } = req.body;

    console.log(`Task requested: ${skill}`, parameters);

    try {
      // Check if it's a native skill
      if (this.skillHandlers[skill]) {
        const result = await this.executeNativeSkill(skill, parameters);
        return res.json(result);
      }

      // Check if it's an MCP tool
      const mcpSkill = this.mcpTools.find(s => s.name === skill);
      if (mcpSkill) {
        const result = await this.executeMCPSkill(skill, parameters);
        return res.json(result);
      }

      // Unknown skill
      res.json({
        success: false,
        error: {
          code: 'UNKNOWN_SKILL',
          message: `Unknown skill: ${skill}. Available skills: ${this.allSkills.map(s => s.name).join(', ')}`
        }
      });

    } catch (error) {
      console.error('Error processing task:', error);
      res.status(500).json({
        success: false,
        error: {
          code: 'INTERNAL_ERROR',
          message: error.message
        }
      });
    }
  }

  /**
   * Execute native skill using handler
   */
  async executeNativeSkill(skillName, parameters) {
    const handler = this.skillHandlers[skillName];
    return await handler(parameters);
  }

  /**
   * Execute MCP-backed skill
   */
  async executeMCPSkill(skillName, parameters) {
    try {
      if (!this.mcpClient) {
        throw new Error('MCP client not initialized');
      }

      const mcpArgs = SchemaTransformer.a2aParamsToMCPArgs(parameters);
      const mcpResult = await this.mcpClient.callTool(skillName, mcpArgs);
      return SchemaTransformer.mcpResultToA2AOutput(mcpResult, skillName);

    } catch (error) {
      return SchemaTransformer.mcpErrorToA2AError(error, skillName);
    }
  }

  /**
   * Get route prefix for this agent (for prefixed endpoints)
   */
  getRoutePrefix() {
    // Override in subclass if needed
    return null;
  }

  /**
   * Start the agent server
   */
  async start() {
    await this.initialize();

    this.app.listen(this.port, () => {
      console.log(`${this.name} listening on port ${this.port}`);
      console.log(`Agent card available at: http://localhost:${this.port}/.well-known/agent.json`);
      console.log(`Access via AgentGateway at: ${this.url}`);
    });
  }
}

module.exports = A2AAgentBase;
