#!/usr/bin/env python3
"""
Middleware to inject user headers into Open WebUI requests
This script adds user information to all outgoing API requests
"""

import os
import sys

# Add this to Open WebUI's backend
# In open-webui/backend/apps/webui/main.py or similar

MIDDLEWARE_CODE = '''
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class UserHeaderMiddleware(BaseHTTPMiddleware):
    """
    Middleware to inject user information into outgoing API requests
    """
    async def dispatch(self, request: Request, call_next):
        # Get user from request state (set by auth middleware)
        user = getattr(request.state, "user", None)

        if user:
            # Add user headers for AgentGateway tracking
            request.state.user_headers = {
                "X-User-Email": getattr(user, "email", ""),
                "X-User-Id": str(getattr(user, "id", "")),
                "X-User-Name": getattr(user, "name", ""),
                "X-User-Role": getattr(user, "role", "user")
            }

            logger.info(f"Adding user headers for: {user.email}")

        response = await call_next(request)
        return response

# Add to your app startup
# app.add_middleware(UserHeaderMiddleware)
'''

print("=" * 70)
print("Open WebUI User Header Middleware")
print("=" * 70)
print()
print("This middleware needs to be added to Open WebUI's backend code.")
print()
print("📝 Steps to add user tracking:")
print()
print("1. Add the middleware code to Open WebUI's backend")
print("2. Modify the OpenAI client to include user headers")
print("3. Restart Open WebUI")
print()
print("=" * 70)
print()
print("Middleware Code:")
print("=" * 70)
print(MIDDLEWARE_CODE)
print()
print("=" * 70)
print()
print("Alternative: Use environment variables")
print("=" * 70)
print()
print("Since modifying Open WebUI code is complex, we can use a simpler approach:")
print()
print("1. Configure Open WebUI to pass user info in request body")
print("2. Use AgentGateway's logging to extract user info")
print("3. Use Jaeger to track by source IP (per-user containers)")
print()
