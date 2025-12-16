FROM python:3.11-slim

WORKDIR /app

# Install required packages
RUN pip install --no-cache-dir requests

# Copy initialization scripts
COPY init-openwebui.py /app/
COPY config.json /app/

# Make script executable
RUN chmod +x /app/init-openwebui.py

CMD ["python", "/app/init-openwebui.py"]
