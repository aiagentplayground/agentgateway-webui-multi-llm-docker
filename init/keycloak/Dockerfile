FROM python:3.11-slim

WORKDIR /app

# Install required packages
RUN pip install --no-cache-dir requests

# Copy initialization scripts
COPY init-keycloak.py /app/
COPY realm-config.json /app/

# Make script executable
RUN chmod +x /app/init-keycloak.py

CMD ["python", "/app/init-keycloak.py"]
