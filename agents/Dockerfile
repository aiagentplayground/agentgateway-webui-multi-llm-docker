FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy agent source files
COPY *.js ./

# Expose ports (will be overridden by docker-compose)
EXPOSE 9001 9002

# Default command (will be overridden by docker-compose)
CMD ["node", "hello-agent.js"]
