FROM ubuntu:22.04

# Install dependencies including Node.js for MCP servers
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    git \
    jq \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Download and install agentgateway
RUN curl -L https://raw.githubusercontent.com/agentgateway/agentgateway/refs/heads/main/common/scripts/get-agentgateway | bash

# Create directory for configuration
RUN mkdir -p /etc/agentgateway

# Copy configuration file
COPY agentgateway.yaml /etc/agentgateway/agentgateway.yaml

# Expose ports
# 3000 - Main gateway port
# 15000 - UI port
EXPOSE 3000 15000

# Set working directory
WORKDIR /etc/agentgateway

# Run agentgateway with config file
CMD ["/usr/local/bin/agentgateway", "-f", "/etc/agentgateway/agentgateway.yaml"]
