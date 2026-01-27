# GitHub Access Setup for Cursor Web Agents

## Status: 📋 **SETUP GUIDE**

**Date:** January 27, 2026

---

## Overview

This guide explains how to configure GitHub access for Cursor Web Agents and enable multiple agents to work in parallel without needing multiple SSH sessions.

---

## Option 1: GitHub Personal Access Token (PAT) - Recommended for Cursor Web Agents

### Why PAT?
- **Simple:** Easy to create and configure
- **Secure:** Can be scoped to specific repositories
- **Works with Cursor:** Cursor can use PATs for GitHub access
- **Multiple Agents:** Each agent can use the same PAT

### Step 1: Create Personal Access Token

1. **Go to GitHub Settings:**
   - Navigate to: https://github.com/settings/tokens
   - Or: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token:**
   - Click "Generate new token" → "Generate new token (classic)"
   - Give it a name: `Cursor Web Agents - SymphAIny`
   - Set expiration: `90 days` (or custom)

3. **Select Scopes:**
   - ✅ **repo** (Full control of private repositories)
     - ✅ repo:status
     - ✅ repo_deployment
     - ✅ public_repo
     - ✅ repo:invite
     - ✅ security_events
   - ✅ **workflow** (Update GitHub Action workflows)
   - ✅ **write:packages** (Upload packages to GitHub Package Registry)
   - ✅ **read:packages** (Download packages from GitHub Package Registry)

4. **Generate Token:**
   - Click "Generate token"
   - **IMPORTANT:** Copy the token immediately (you won't see it again!)
   - Store it securely

### Step 2: Configure Cursor with PAT

**In Cursor Settings:**

1. **Open Cursor Settings:**
   - Cursor → Settings → Features → GitHub

2. **Add GitHub Token:**
   - Find "GitHub Personal Access Token" field
   - Paste your PAT
   - Save settings

**OR via Cursor Config File:**

Create/update `.cursor/settings.json`:

```json
{
  "github": {
    "personalAccessToken": "ghp_YOUR_TOKEN_HERE",
    "repository": "Aaron-Lilly/symphainy-prod"
  }
}
```

**⚠️ Security Note:** Add `.cursor/settings.json` to `.gitignore` if it contains tokens!

### Step 3: Test GitHub Access

```bash
# Test from command line
cd /home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric
git remote -v  # Should show your repo

# Test with curl (using PAT)
curl -H "Authorization: token YOUR_PAT" https://api.github.com/user
```

---

## Option 2: GitHub App (More Secure, More Complex)

### Why GitHub App?
- **More Secure:** Fine-grained permissions
- **Better for Organizations:** Can be installed on multiple repos
- **Audit Trail:** Better tracking of who did what

### Step 1: Create GitHub App

1. **Go to GitHub App Settings:**
   - Navigate to: https://github.com/settings/apps
   - Or: GitHub → Settings → Developer settings → GitHub Apps

2. **Create New App:**
   - Click "New GitHub App"
   - **Name:** `SymphAIny Cursor Web Agents`
   - **Homepage URL:** Your repo URL
   - **Webhook URL:** (Optional, leave blank for now)
   - **Webhook secret:** (Optional, leave blank for now)

3. **Set Permissions:**
   - **Repository permissions:**
     - ✅ Contents: Read and write
     - ✅ Metadata: Read-only
     - ✅ Pull requests: Read and write
     - ✅ Issues: Read and write
   - **Account permissions:** (Leave as default)

4. **Where can this GitHub App be installed?**
   - Select: "Only on this account"

5. **Create App:**
   - Click "Create GitHub App"

### Step 2: Install GitHub App

1. **Install on Repository:**
   - Go to your app settings
   - Click "Install App"
   - Select your account
   - Select repository: `symphainy-prod`
   - Click "Install"

2. **Generate Private Key:**
   - In app settings, click "Generate a private key"
   - Download the `.pem` file
   - Store it securely

3. **Get App ID:**
   - Note your App ID (shown in app settings)

### Step 3: Configure Cursor with GitHub App

**In Cursor Settings:**

1. **Open Cursor Settings:**
   - Cursor → Settings → Features → GitHub

2. **Add GitHub App Credentials:**
   - App ID: Your app ID
   - Private Key: Path to your `.pem` file
   - Installation ID: Your installation ID

**OR via Cursor Config File:**

```json
{
  "github": {
    "appId": "YOUR_APP_ID",
    "privateKeyPath": "/path/to/your/app.pem",
    "installationId": "YOUR_INSTALLATION_ID",
    "repository": "Aaron-Lilly/symphainy-prod"
  }
}
```

---

## Option 3: SSH Keys (Current Setup - May Need Adjustment)

### Current Setup
- You're using SSH-based access: `git@github.com:Aaron-Lilly/symphainy-prod.git`
- This works for command-line git
- Cursor Web Agents may need additional configuration

### For Cursor Web Agents with SSH

1. **Ensure SSH Agent is Running:**
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa  # or your key path
```

2. **Configure SSH for Cursor:**
   - Cursor may need SSH agent forwarding
   - Or use SSH config file

3. **Test SSH Access:**
```bash
ssh -T git@github.com
# Should see: "Hi Aaron-Lilly! You've successfully authenticated..."
```

**Note:** SSH may be less ideal for Cursor Web Agents as they may need direct API access.

---

## Multiple Agents Configuration

### How Multiple Agents Work

Cursor Web Agents can work in parallel by:
1. **Using Same Repository:** All agents access the same GitHub repo
2. **Working on Different Branches:** Each agent works on its own branch
3. **Creating Separate PRs:** Each agent creates its own PR
4. **No Conflicts:** Agents work on different solution components

### Recommended Setup for Multiple Agents

**Branch Strategy:**
```
main (or symphainy-platform-v2)
├── agent-security-solution      # Security Solution Agent
├── agent-coexistence-solution   # Coexistence Solution Agent
├── agent-control-tower-solution # Control Tower Solution Agent
└── agent-platform-mvp-solution # Platform MVP Solution Agent
```

**Each Agent:**
1. Creates its own branch from main
2. Works on its solution component
3. Creates PR when done
4. You review and merge

### Configuration for Multiple Agents

**Option A: One PAT for All Agents (Simplest)**
- Create one PAT
- All agents use the same PAT
- Each agent works on its own branch
- ✅ Simple
- ⚠️ Less granular control

**Option B: Separate PATs for Each Agent (More Secure)**
- Create separate PAT for each agent
- Each agent has its own credentials
- Better audit trail
- ✅ More secure
- ⚠️ More complex

**Option C: GitHub App (Best for Organizations)**
- One GitHub App
- All agents use the same app
- Fine-grained permissions
- ✅ Most secure
- ✅ Best audit trail
- ⚠️ Most complex setup

---

## Cursor Web Agents Configuration

### Enable Multiple Agents in Cursor

**In Cursor Settings:**

1. **Open Cursor Settings:**
   - Cursor → Settings → Features → Agents

2. **Enable Multiple Agents:**
   - Check "Allow multiple agents"
   - Set max concurrent agents (e.g., 4)

3. **Configure Agent Workspaces:**
   - Each agent can have its own workspace
   - Or all agents share the same workspace

### Agent Workspace Configuration

**Option 1: Shared Workspace (Simpler)**
- All agents work in same folder
- Each agent works on different files/branches
- ✅ Simpler
- ⚠️ Potential conflicts if not careful

**Option 2: Separate Workspaces (Safer)**
- Each agent has its own workspace folder
- Agents work independently
- ✅ No conflicts
- ⚠️ More complex setup

**Recommended:** Shared workspace with branch-based isolation

---

## Quick Setup Checklist

### For PAT (Recommended)

- [ ] Create GitHub Personal Access Token
- [ ] Configure PAT in Cursor settings
- [ ] Test GitHub access
- [ ] Enable multiple agents in Cursor
- [ ] Configure agent workspaces
- [ ] Test with one agent first
- [ ] Scale to multiple agents

### For GitHub App

- [ ] Create GitHub App
- [ ] Install on repository
- [ ] Generate private key
- [ ] Configure in Cursor settings
- [ ] Test GitHub access
- [ ] Enable multiple agents
- [ ] Test with one agent first
- [ ] Scale to multiple agents

---

## Troubleshooting

### Issue: Agents Can't Access GitHub

**Solution:**
- Check PAT/App credentials in Cursor settings
- Verify repository access
- Test GitHub API access manually
- Check network/firewall settings

### Issue: Multiple Agents Conflict

**Solution:**
- Ensure each agent works on different branch
- Use branch-based isolation
- Review PRs before merging
- Use separate workspaces if needed

### Issue: SSH Not Working with Cursor

**Solution:**
- Switch to PAT (recommended for Cursor Web Agents)
- Or configure SSH agent forwarding
- Or use GitHub App

---

## Security Best Practices

1. **Never Commit Tokens:**
   - Add `.cursor/settings.json` to `.gitignore`
   - Use environment variables when possible
   - Rotate tokens regularly

2. **Use Least Privilege:**
   - Only grant necessary permissions
   - Use separate PATs for different purposes
   - Review token permissions regularly

3. **Monitor Access:**
   - Review GitHub audit logs
   - Monitor agent activity
   - Set up alerts for unusual activity

---

## Next Steps

1. **Choose Access Method:** PAT (recommended) or GitHub App
2. **Configure Cursor:** Add credentials to Cursor settings
3. **Test Access:** Verify GitHub access works
4. **Enable Multiple Agents:** Configure in Cursor settings
5. **Test with One Agent:** Start with one agent, then scale

---

**Last Updated:** January 27, 2026  
**Owner:** Development Team
