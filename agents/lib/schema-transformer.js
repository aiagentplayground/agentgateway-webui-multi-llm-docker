/**
 * Schema Transformer
 * Converts between MCP tool schemas and A2A skill schemas
 */

class SchemaTransformer {
  /**
   * Convert MCP tool schema to A2A skill format
   * @param {object} mcpTool - MCP tool object with name, description, inputSchema
   * @returns {object} A2A skill object
   */
  static mcpToolToA2ASkill(mcpTool) {
    return {
      name: mcpTool.name,
      description: mcpTool.description || `MCP tool: ${mcpTool.name}`,
      parameters: mcpTool.inputSchema || {
        type: 'object',
        properties: {},
        required: []
      },
      // Mark as MCP-backed for routing logic
      _mcpBacked: true
    };
  }

  /**
   * Convert A2A parameters to MCP arguments
   * @param {object} a2aParams - Parameters from A2A task request
   * @returns {object} Arguments for MCP tool call
   */
  static a2aParamsToMCPArgs(a2aParams) {
    // Direct pass-through in most cases
    // Can add transformation logic if needed
    return a2aParams || {};
  }

  /**
   * Convert MCP response to A2A output format
   * @param {object} mcpResult - Result from MCP tool call
   * @param {string} toolName - Name of the tool that was called
   * @returns {object} A2A output format
   */
  static mcpResultToA2AOutput(mcpResult, toolName) {
    // MCP returns: { content: [{ type: 'text', text: '...' }, ...] }
    // A2A expects: { success: true, output: { type: 'text', text: '...' } }

    if (!mcpResult || !mcpResult.content) {
      return {
        success: true,
        output: {
          type: 'text',
          text: `Tool ${toolName} executed successfully`,
          data: mcpResult
        }
      };
    }

    // Extract first content item (most common case)
    const primaryContent = mcpResult.content[0];

    return {
      success: true,
      output: {
        type: primaryContent.type || 'text',
        text: primaryContent.text || JSON.stringify(primaryContent),
        data: {
          toolName,
          fullResult: mcpResult.content
        }
      }
    };
  }

  /**
   * Convert MCP error to A2A error format
   * @param {Error} error - Error from MCP call
   * @param {string} toolName - Name of the tool that failed
   * @returns {object} A2A error format
   */
  static mcpErrorToA2AError(error, toolName) {
    return {
      success: false,
      error: {
        code: error.code || 'MCP_TOOL_ERROR',
        message: `MCP tool '${toolName}' failed: ${error.message}`,
        details: error.data
      }
    };
  }
}

module.exports = SchemaTransformer;
