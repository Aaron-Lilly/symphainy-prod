# Quick Start: GitHub Access for Multiple Cursor Web Agents

## 🚀 Fastest Path to Multiple Agents

### Step 1: Create GitHub Personal Access Token (5 minutes)

1. **Go to:** https://github.com/settings/tokens
2. **Click:** "Generate new token" → "Generate new token (classic)"
3. **Name:** `Cursor Web Agents - SymphAIny`
4. **Expiration:** 90 days (or custom)
5. **Scopes:** Check ✅ **repo** (all sub-options)
6. **Click:** "Generate token"
7. **Copy token immediately** (starts with `ghp_`)

### Step 2: Configure Cursor (2 minutes)

**Option A: Via Cursor UI (Easiest)**
1. Open Cursor
2. Go to: **Settings** → **Features** → **GitHub**
3. Paste your PAT in "GitHub Personal Access Token"
4. Save

**Option B: Via Config File**
```bash
cd /home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric
cat > .cursor/settings.json << 'EOF'
{
  "github": {
    "personalAccessToken": "ghp_YOUR_TOKEN_HERE",
    "repository": "Aaron-Lilly/symphainy-prod"
  }
}
EOF
```

**⚠️ IMPORTANT:** Add to `.gitignore`:
```bash
echo ".cursor/settings.json" >> .gitignore
```

### Step 3: Enable Multiple Agents in Cursor (1 minute)

1. **Open Cursor Settings**
2. **Go to:** Features → Agents
3. **Enable:** "Allow multiple agents"
4. **Set:** Max concurrent agents = 4
5. **Workspace:** Shared workspace (recommended)

### Step 4: Test GitHub Access (1 minute)

```bash
# Test from command line
cd /home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric
git remote -v  # Should show your repo

# Test API access (replace YOUR_PAT)
curl -H "Authorization: token YOUR_PAT" https://api.github.com/user
```

### Step 5: Configure Agent Branches

Each agent will work on its own branch:

- **Security Solution Agent** → `agent-security-solution`
- **Coexistence Solution Agent** → `agent-coexistence-solution`
- **Control Tower Solution Agent** → `agent-control-tower-solution`
- **Platform MVP Solution Agent** → `agent-platform-mvp-solution`

**How it works:**
- Each agent creates its own branch
- Works independently on its solution component
- Creates PR when done
- You review and merge

---

## ✅ That's It!

**Total Time:** ~10 minutes

**Result:**
- ✅ GitHub access configured
- ✅ Multiple agents enabled
- ✅ No need for multiple SSH sessions
- ✅ All agents work in same workspace
- ✅ Each agent on its own branch

---

## How Multiple Agents Work

**No Multiple Windows Needed!**

1. **One Cursor Window:** All agents work in the same Cursor workspace
2. **Branch Isolation:** Each agent works on its own branch
3. **Parallel Execution:** Agents work simultaneously
4. **No Conflicts:** Different branches = no file conflicts
5. **PR Review:** You review each agent's PR separately

**Example:**
```
You: "Security Solution Agent, create Security Solution contract"
→ Agent creates branch: agent-security-solution
→ Agent creates contract file
→ Agent creates PR

You: "Coexistence Solution Agent, create Coexistence Solution contract"
→ Agent creates branch: agent-coexistence-solution
→ Agent creates contract file
→ Agent creates PR

Both agents work simultaneously, no conflicts!
```

---

## Troubleshooting

### "Agents can't access GitHub"
- Check PAT is correct in Cursor settings
- Verify PAT has `repo` scope
- Test API access manually

### "Multiple agents conflict"
- Ensure each agent uses different branch
- Check branch names are unique
- Review PRs before merging

### "SSH still required"
- Cursor Web Agents use GitHub API, not SSH
- PAT replaces SSH for agent access
- Your SSH setup still works for manual git commands

---

## Next Steps

1. ✅ Create PAT (done above)
2. ✅ Configure Cursor (done above)
3. ✅ Test access (done above)
4. ⏳ Start creating contracts
5. ⏳ Spin up agents

**Ready to go!** 🚀
