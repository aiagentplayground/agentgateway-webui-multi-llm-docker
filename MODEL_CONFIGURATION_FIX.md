# Model Configuration Fix

## Problem

Models were not appearing in Open WebUI even though they were configured in the database. The issue had TWO root causes:

### 1. Missing `api_configs` Configuration

Open WebUI requires models to be configured in the `openai.api_configs` section of the config JSON with specific fields:

```json
{
  "openai": {
    "api_configs": {
      "0": {
        "enable": true,
        "model_ids": ["claude-haiku-4-5-20251001"],
        "connection_type": "external",
        "auth_type": "bearer"
      }
    }
  }
}
```

The index ("0", "1", "2", "3") corresponds to the index in `OPENAI_API_BASE_URLS` array.

**Our scripts were missing this configuration entirely!**

### 2. AgentGateway Doesn't Implement `/v1/models` Endpoint

Open WebUI tries to auto-discover models by calling the `/models` endpoint on each API base URL:
- `http://agentgateway:3000/anthropic/v1/models` → 404 Not Found
- `http://agentgateway:3000/openai/v1/models` → 501 Not Implemented

This caused errors and prevented model discovery.

**Solution**: Disabled automatic model fetching with `ENABLE_MODEL_FILTER: false`

## How The Fix Was Discovered

The user manually configured grok-4-latest through the Open WebUI admin panel, which created the correct `api_configs` structure. By examining the database, we discovered:

```json
"2": {
  "enable": true,
  "tags": [],
  "prefix_id": "",
  "model_ids": ["grok-4-latest"],
  "connection_type": "external",
  "auth_type": "bearer"
}
```

This revealed the missing configuration that made models work!

## What Was Fixed

### 1. Updated `scripts/configure-openwebui-connections.py`
Added the critical `api_configs` section and disabled automatic model fetching.

### 2. Updated `scripts/configure-models-db.py`
Added the same `api_configs` configuration.

### 3. Updated `init/openwebui/init-openwebui.py`
Completely rewrote the `configure_models()` method to:
- Directly update the database (not use broken API endpoints)
- Include the `api_configs` configuration
- Add models to the `model` table
- Disable automatic model fetching

## Current Configuration

All 4 models are now properly configured:

| Index | Provider | Model ID | Endpoint |
|-------|----------|----------|----------|
| 0 | Anthropic | claude-haiku-4-5-20251001 | http://agentgateway:3000/anthropic/v1 |
| 1 | OpenAI | gpt-5.2-2025-12-11 | http://agentgateway:3000/openai/v1 |
| 2 | xAI | grok-4-latest | http://agentgateway:3000/xai/v1 |
| 3 | Gemini | gemini-3-pro-preview | http://agentgateway:3000/gemini/v1 |

## How to Use

### Manual Configuration (Recommended for README)
```bash
python3 scripts/configure-models-db.py
docker-compose restart open-webui
```

### Automatic Configuration (On Startup)
The `openwebui-init` container now properly configures models on startup. To re-run:
```bash
docker-compose up openwebui-init
```

### Verify Models Are Working
1. Go to http://localhost:8888
2. Log in as admin@example.com / Admin123!
3. Click the model selector dropdown at the top of the chat interface
4. All 4 models should be visible and selectable

## Database Structure

### Config Table
```json
{
  "ENABLE_OPENAI_API": true,
  "OPENAI_API_BASE_URLS": ["url1", "url2", ...],
  "OPENAI_API_KEYS": ["key1", "key2", ...],
  "openai": {
    "enable": true,
    "api_base_urls": ["url1", "url2", ...],
    "api_keys": ["key1", "key2", ...],
    "api_configs": {
      "0": {
        "enable": true,
        "model_ids": ["model-id"],
        "connection_type": "external",
        "auth_type": "bearer"
      }
    }
  },
  "ENABLE_MODEL_FILTER": false
}
```

### Model Table
Each model needs an entry with:
- `id`: Model identifier
- `name`: Display name
- `user_id`: Empty string for system-wide
- `base_model_id`: Same as id
- `meta`: JSON with profile_image_url, description, capabilities
- `params`: JSON with api_base_url, api_key, stream
- `is_active`: 1 (enabled)
- `access_control`: JSON with empty read/write permissions for public access

## Key Learnings

1. **Open WebUI requires THREE places to configure models**:
   - `OPENAI_API_BASE_URLS` and `OPENAI_API_KEYS` (top level)
   - `openai.api_configs` with `model_ids` (CRITICAL!)
   - `model` table entries

2. **The `api_configs` section is the KEY** - without it, models won't appear even if they're in the database

3. **AgentGateway doesn't implement `/v1/models`** - must disable auto-discovery

4. **Manual UI configuration revealed the solution** - always check what the UI creates when you configure something manually!
