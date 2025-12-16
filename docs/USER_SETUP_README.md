# Open WebUI User Setup Guide

This guide explains how to automatically create users and organize them into teams in Open WebUI.

## Overview

The setup script creates 5 users organized into 3 teams:

### Teams and Users

**Marketing Team (2 users)**
- Sarah Johnson - `sarah.marketing@example.com`
- Mike Chen - `mike.marketing@example.com`

**Platform Team (2 users)**
- Alex Rivera - `alex.platform@example.com`
- Jordan Kim - `jordan.platform@example.com`

**Security Team (1 user)**
- Taylor Morgan - `taylor.security@example.com`

## Prerequisites

1. Open WebUI must be running:
   ```bash
   docker-compose up -d open-webui
   ```

2. Python 3 and requests library:
   ```bash
   pip install requests
   ```

## Quick Start

Run the setup script:

```bash
python3 setup-users.py
```

The script will:
1. Create an admin user (or use existing)
2. Create 5 team users
3. Display a summary with credentials

## Customization

### Changing Team Assignments

Edit `setup-users.py` and modify the `USERS` list:

```python
USERS = [
    {
        "email": "user@example.com",
        "password": "password123",
        "name": "User Name",
        "team": "marketing",  # or "platform", "security"
        "role": "user"
    },
    # Add more users...
]
```

### Changing Admin Credentials

Edit these variables in `setup-users.py`:

```python
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "changeme123"  # CHANGE THIS!
ADMIN_NAME = "Admin User"
```

**⚠️ IMPORTANT:** Change the admin password after first login!

## Default Passwords

For testing purposes, default passwords are set per team:
- Marketing users: `marketing123`
- Platform users: `platform123`
- Security users: `security123`

**⚠️ PRODUCTION:** Change these passwords before deploying to production!

## Accessing Open WebUI

- **URL:** http://localhost:8888
- **Admin Panel:** http://localhost:8888/admin

### First-Time Login

1. Go to http://localhost:8888
2. Sign in with any user credentials
3. Users can change their passwords in Settings

## Team Management

Open WebUI doesn't have built-in team features, but users are organized by:
- Email naming convention (e.g., `@team.example.com`)
- Display names
- Metadata (can be extended)

### Viewing Users

As an admin:
1. Sign in with admin credentials
2. Go to Admin Panel (http://localhost:8888/admin)
3. Navigate to Users section

## Troubleshooting

### Script Fails to Connect

```bash
# Check if Open WebUI is running
docker-compose ps open-webui

# Check logs
docker-compose logs open-webui
```

### Users Already Exist

The script will skip existing users and continue with the rest.

### Permission Errors

Make sure you're using the admin credentials when creating users.

## API Reference

The script uses Open WebUI's REST API:

- `POST /api/v1/auths/signup` - Create user
- `POST /api/v1/auths/signin` - Sign in
- `GET /api/v1/users/` - List users (admin only)

## Advanced Configuration

### Environment Variables

You can use environment variables instead of hardcoding credentials:

```bash
export OPENWEBUI_ADMIN_EMAIL="admin@example.com"
export OPENWEBUI_ADMIN_PASSWORD="secure_password"
python3 setup-users.py
```

### Bulk User Import

To import users from a CSV file, modify the script to read from:

```python
import csv

with open('users.csv', 'r') as f:
    reader = csv.DictReader(f)
    USERS = list(reader)
```

CSV format:
```csv
email,password,name,team,role
user1@example.com,pass123,User One,marketing,user
user2@example.com,pass123,User Two,platform,user
```

## Security Best Practices

1. **Change Default Passwords**
   - Admin password should be changed immediately
   - User passwords should be changed on first login

2. **Use Strong Passwords**
   - Minimum 12 characters
   - Mix of letters, numbers, and symbols

3. **Restrict Admin Access**
   - Limit who has admin credentials
   - Use admin account only for administration

4. **Enable 2FA** (if available in your Open WebUI version)
   - Check Open WebUI settings for 2FA options

5. **Regular Audits**
   - Review user list regularly
   - Remove inactive accounts

## Integration with AgentGateway

All users can access the AI models through AgentGateway:

- **Anthropic Claude:** Available via model selector
- **OpenAI GPT-5.2:** Available via model selector
- **xAI Grok:** Available via model selector
- **Google Gemini:** Available via model selector

Each model is already configured in docker-compose.yml with rate limiting through AgentGateway.

## Support

For issues with:
- **Open WebUI:** https://github.com/open-webui/open-webui
- **AgentGateway:** https://github.com/agentgateway/agentgateway

## Next Steps

After setting up users:

1. Test login with each user account
2. Have users change their passwords
3. Configure team-specific models or rate limits in AgentGateway
4. Set up monitoring and usage tracking
5. Create team-specific documentation
