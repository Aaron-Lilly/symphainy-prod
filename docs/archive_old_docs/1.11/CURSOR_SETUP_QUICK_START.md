# Cursor Web Agents - Quick Start Checklist

**Time:** ~15 minutes  
**Difficulty:** Easy

---

## ✅ Step-by-Step Setup

### 1. Create GitHub Personal Access Token (5 min)

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `Cursor Web Agents - Symphainy`
4. Select scopes:
   - ✅ `repo` (Full control)
   - ✅ `workflow` (Update workflows)
5. Click "Generate token"
6. **Copy token** (you won't see it again!)

### 2. Configure Cursor (2 min)

1. Open Cursor
2. Go to Settings → GitHub Integration
3. Paste your Personal Access Token
4. Save

### 3. Add Old Repo Access Token (3 min)

1. Go to: https://github.com/Aaron-Lilly/symphainy-prod/settings/secrets/actions
2. Click "New repository secret"
3. Name: `OLD_REPO_ACCESS_TOKEN`
4. Value: Another PAT with access to your old repo
5. Click "Add secret"

### 4. Update Migration Config (2 min)

1. Edit `.cursor/migration-mapping.json`
2. Update `source_repos` with your old repo name
3. Update `file_mappings` with correct paths

### 5. Test It! (3 min)

1. Open Cursor in this repo
2. Ask agent: "List all Python files in symphainy_platform"
3. If it works, you're done! ✅

---

## 🔧 Multi-Repo Access

### For Code Migration:

**Option 1: Use the same PAT**
- If your PAT has access to both repos, you're done!

**Option 2: Use GitHub App**
- See full guide: `docs/CURSOR_WEB_AGENTS_SETUP.md`

---

## 🚀 Using the Multi-Repo Sync Workflow

1. Go to: https://github.com/Aaron-Lilly/symphainy-prod/actions
2. Click "Sync from Old Repository"
3. Click "Run workflow"
4. Fill in:
   - Source repo: `YOUR_ORG/old-repo-name`
   - Source path: (optional)
   - Target path: (optional)
5. Click "Run workflow"
6. Review the PR it creates

---

## ❓ Troubleshooting

**"Agent cannot access repository"**
- Check token has `repo` scope
- Verify token hasn't expired
- Check repo is accessible

**"Cannot access old repo"**
- Verify `OLD_REPO_ACCESS_TOKEN` secret exists
- Check token has access to old repo
- Update workflow with correct repo name

---

## 📚 Full Documentation

See `docs/CURSOR_WEB_AGENTS_SETUP.md` for complete details.

---

**Last Updated:** January 2026
