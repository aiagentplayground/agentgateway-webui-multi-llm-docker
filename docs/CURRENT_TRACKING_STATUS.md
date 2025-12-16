# Current User Tracking Status

## Summary

✅ **Working:** AgentGateway is successfully routing requests and capturing traces in Jaeger
❌ **Missing:** User identity headers are not being passed from Open WebUI to AgentGateway

## What You Can Track Right Now

### 1. Overall Platform Usage

```bash
python3 scripts/track-users-openwebui.py
```

**Shows:**
- Total LLM requests (last 24h)
- Requests by provider (Anthropic, OpenAI, xAI, Gemini)
- Success vs. error rates
- HTTP status code distribution

**Example Output:**
```
Total Requests:  14
Successful:      10
Errors:          4

By Provider:
  • Anthropic: 10 requests (71.4%)
```

### 2. Individual Request Traces (Jaeger)

**Access:** http://localhost:16686

**What you can see:**
- Exact timestamp of each request
- Response time and duration
- Which LLM provider was used
- Token usage (input/output tokens)
- HTTP status codes
- Source IP address

**How to use:**
1. Service: Select `agentgateway`
2. Lookback: Last Hour / Last 24 Hours
3. Sort by time
4. Click any trace to see full details

### 3. Open WebUI Admin Panel

**Access:** http://localhost:8888 → Admin Panel

**What you can see:**
- User list and roles
- When users last logged in
- User creation dates
- User permissions

## What You CANNOT Track (Without Headers)

❌ Which specific user made which LLM request
❌ Token usage per user
❌ Cost attribution per user/team
❌ Provider preferences by user

## Why User Tracking Isn't Working

Open WebUI doesn't pass user identification headers (`X-User-Email`, `X-User-Id`, etc.) to backend API providers by default.

**What we configured:**
- ✅ AgentGateway is ready to capture user headers (if sent)
- ✅ Jaeger tracing is working perfectly
- ✅ Prometheus metrics are being collected
- ❌ Open WebUI needs customization to pass headers

## Solutions to Enable Full User Tracking

### Solution 1: Modify Open WebUI Code (Advanced)

Add middleware to Open WebUI's backend to inject user headers:

**File:** `/app/backend/apps/webui/main.py`

```python
from starlette.middleware.base import BaseHTTPMiddleware

class UserHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user = getattr(request.state, "user", None)
        if user:
            # Inject into outgoing requests to AgentGateway
            request.headers["X-User-Email"] = user.email
            request.headers["X-User-Id"] = str(user.id)
        response = await call_next(request)
        return response

app.add_middleware(UserHeaderMiddleware)
```

**Pros:** Full per-user tracking
**Cons:** Requires modifying Docker image and rebuilding

### Solution 2: Use Open WebUI Functions (Recommended)

Open WebUI supports "Functions" which can modify requests:

1. Go to Admin Panel → Workspace → Functions
2. Create new function with this code:

```javascript
export default async function addUserHeaders(request, user) {
    // Add user info to request headers
    request.headers['X-User-Email'] = user.email;
    request.headers['X-User-Id'] = user.id;
    request.headers['X-User-Name'] = user.name;
    return request;
}
```

3. Enable the function globally

**Pros:** No code changes needed
**Cons:** Depends on Open WebUI's function system supporting header injection

### Solution 3: Proxy Layer (Intermediate)

Add an nginx proxy between Open WebUI and AgentGateway that injects headers:

**nginx.conf:**
```nginx
location /api/ {
    proxy_pass http://agentgateway:3000/;
    proxy_set_header X-User-Email $http_x_forwarded_user;
    # Additional header mapping
}
```

**Pros:** Clean separation, no app changes
**Cons:** Adds complexity

### Solution 4: Accept Limitations (Current State)

Use what's available:
- Track overall platform usage
- View detailed traces in Jaeger
- Use Open WebUI's built-in user management
- Correlate by timing/IP address when needed

**Pros:** Works now, no changes needed
**Cons:** No automatic per-user attribution

## Current Workaround

Since you asked about mike.chen's activity:

1. **Note the time** when mike.chen makes a request
2. **Open Jaeger** at http://localhost:16686
3. **Search** for traces around that time:
   - Service: `agentgateway`
   - Time range: Narrow to when request was made
4. **Identify** the trace by:
   - Timestamp matching
   - Source IP (if mike.chen has unique IP)
   - Request details (model, prompt length)

### Example: Finding Mike Chen's Request

```bash
# 1. Mike makes request at 17:28:04
# 2. Check AgentGateway logs
docker-compose logs agentgateway | grep "17:28:04"

# Result shows:
# 2025-12-16T17:28:04.844547Z ... trace.id=eaa41568721f8185d7cecbf9e496662a
#   http.path=/anthropic/v1/chat/completions ... duration=4738ms
#   gen_ai.usage.input_tokens=41 gen_ai.usage.output_tokens=281

# 3. Search Jaeger for that trace ID
# http://localhost:16686/trace/eaa41568721f8185d7cecbf9e496662a
```

## Recommendations

### For Development/Testing (Current):
✅ Use Solution 4 (current workaround)
✅ Run `python3 scripts/track-users-openwebui.py` for daily summaries
✅ Use Jaeger for detailed trace analysis

### For Production:
🔧 Implement Solution 2 (Open WebUI Functions) if available
🔧 Or Solution 1 (modify Open WebUI) for full control
🔧 Or Solution 3 (proxy layer) for clean architecture

## Next Steps

1. **Verify your setup works:**
   ```bash
   python3 scripts/track-users-openwebui.py
   ```

2. **Check Jaeger traces:**
   - Open http://localhost:16686
   - Service: `agentgateway`
   - Verify you see your requests

3. **Explore Open WebUI admin:**
   - Check if Functions feature is available
   - Review user activity logs

4. **Decide on approach:**
   - Accept current limitations (easiest)
   - OR implement one of the solutions above

## Support

- View this guide: `docs/CURRENT_TRACKING_STATUS.md`
- Check Jaeger guide: `docs/USER_TRACKING_JAEGER.md`
- Run tracking script: `scripts/track-users-openwebui.py`
- View logs: `docker-compose logs agentgateway | grep "route_rule"`
