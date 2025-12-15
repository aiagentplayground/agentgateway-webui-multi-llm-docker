/**
 * MCP Client Module
 * Handles JSON-RPC 2.0 communication with AgentGateway MCP endpoint
 */
const http = require('http');

class MCPClient {
  constructor(config = {}) {
    this.endpoint = config.endpoint || 'http://agentgateway:3000/mcp/stdio';
    this.protocolVersion = '2024-11-05';
    this.requestId = 0;
    this.timeout = config.timeout || 10000; // 10s default
    this.maxRetries = config.maxRetries || 3;
    this.retryDelay = config.retryDelay || 1000;
    this.initialized = false;
    this.serverInfo = null;
  }

  /**
   * Initialize connection to MCP server
   * Must be called before other operations
   */
  async initialize(clientInfo = { name: 'a2a-agent', version: '1.0.0' }) {
    const request = {
      jsonrpc: '2.0',
      id: this.getNextRequestId(),
      method: 'initialize',
      params: {
        protocolVersion: this.protocolVersion,
        capabilities: {},
        clientInfo
      }
    };

    const response = await this._sendRequest(request);
    this.initialized = true;
    this.serverInfo = response.result;
    return this.serverInfo;
  }

  /**
   * List all available tools from MCP server
   * Returns array of tool schemas
   */
  async listTools() {
    if (!this.initialized) {
      await this.initialize();
    }

    const request = {
      jsonrpc: '2.0',
      id: this.getNextRequestId(),
      method: 'tools/list'
    };

    const response = await this._sendRequest(request);
    return response.result.tools || [];
  }

  /**
   * Call a specific MCP tool
   * @param {string} toolName - Name of the tool to call
   * @param {object} args - Arguments for the tool
   */
  async callTool(toolName, args = {}) {
    if (!this.initialized) {
      await this.initialize();
    }

    const request = {
      jsonrpc: '2.0',
      id: this.getNextRequestId(),
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: args
      }
    };

    const response = await this._sendRequest(request);
    return response.result;
  }

  /**
   * Send JSON-RPC request with retry logic
   * @private
   */
  async _sendRequest(request, retryCount = 0) {
    try {
      return await this._makeHttpRequest(request);
    } catch (error) {
      if (retryCount < this.maxRetries) {
        console.log(`MCP request failed, retrying (${retryCount + 1}/${this.maxRetries})...`);
        await this._sleep(this.retryDelay * (retryCount + 1)); // Exponential backoff
        return this._sendRequest(request, retryCount + 1);
      }
      throw error;
    }
  }

  /**
   * Make HTTP request to MCP endpoint
   * @private
   */
  async _makeHttpRequest(request) {
    return new Promise((resolve, reject) => {
      const url = new URL(this.endpoint);
      const postData = JSON.stringify(request);

      const options = {
        hostname: url.hostname,
        port: url.port || 3000,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'mcp-protocol-version': this.protocolVersion,
          'Content-Length': Buffer.byteLength(postData)
        },
        timeout: this.timeout
      };

      const req = http.request(options, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          try {
            const response = JSON.parse(data);

            if (response.error) {
              const error = new Error(response.error.message);
              error.code = response.error.code;
              error.data = response.error.data;
              reject(error);
            } else {
              resolve(response);
            }
          } catch (error) {
            reject(new Error(`Failed to parse MCP response: ${error.message}`));
          }
        });
      });

      req.on('error', (error) => {
        reject(new Error(`MCP request failed: ${error.message}`));
      });

      req.on('timeout', () => {
        req.destroy();
        reject(new Error(`MCP request timed out after ${this.timeout}ms`));
      });

      req.write(postData);
      req.end();
    });
  }

  getNextRequestId() {
    return ++this.requestId;
  }

  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

module.exports = MCPClient;
