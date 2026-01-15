# Cursor Web Agents Setup Guide

**Date:** January 2026  
**Status:** 📋 Setup Instructions

---

## Overview

This guide walks you through setting up Cursor web agents to work with your GitHub repository and enable multi-repo access for code migration between projects.

---

## Part 1: Basic Cursor Web Agent Setup

### Step 1: GitHub Integration in Cursor

Cursor web agents need access to your GitHub repository. Here's how to set it up:

#### Option A: GitHub Personal Access Token (PAT) - Recommended for Development

1. **Create a GitHub Personal Access Token:**
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Name it: `Cursor Web Agents - Symphainy`
   - Select scopes:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
     - ✅ `read:org` (Read org membership - if using org repos)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again)

2. **Add Token to Cursor:**
   - Open Cursor Settings
   - Navigate to "GitHub Integration" or "Web Agents"
   - Paste your Personal Access Token
   - Save settings

#### Option B: GitHub App (Recommended for Production/Teams)

1. **Create a GitHub App:**
   - Go to your organization/user settings → Developer settings → GitHub Apps
   - Click "New GitHub App"
   - Name: `Symphainy Cursor Agents`
   - Homepage URL: Your repo URL
   - Set permissions:
     - **Repository permissions:**
       - Contents: Read & Write
       - Metadata: Read-only
       - Pull requests: Read & Write
       - Issues: Read & Write
       - Workflows: Read & Write
   - Where can this GitHub App be installed: "Only on this account"
   - Click "Create GitHub App"

2. **Install the App:**
   - After creating, click "Install App"
   - Select repositories (or all repos)
   - Click "Install"

3. **Generate Private Key:**
   - Download the private key
   - Store it securely (use GitHub Secrets if using in CI/CD)

4. **Configure in Cursor:**
   - Use the App ID and Private Key in Cursor's GitHub App settings

---

## Part 2: Multi-Repo Access Setup

To enable Cursor web agents to move/rebuild code between projects (e.g., from old project to new project), you need to grant access to multiple repositories.

### Method 1: Personal Access Token with Multiple Repos

If using a PAT (Option A above), the token already has access to all repos you have access to. Just ensure:

1. **Token has `repo` scope** (already selected above)
2. **You have access to both repositories:**
   - Old project repo (source)
   - New project repo (destination: `symphainy-prod`)

### Method 2: Organization-Level Access (Best for Teams)

1. **Add Agent User to Organization:**
   - Go to Organization Settings → Members
   - Add the user/service account
   - Assign role: "Member" or "Outside Collaborator"

2. **Grant Repository Access:**
   - Organization Settings → Third-party access
   - Or: Repository Settings → Collaborators (for each repo)

### Method 3: GitHub App with Multiple Repos

When creating the GitHub App (Option B above):

1. **During Installation:**
   - Select "All repositories" OR
   - Select specific repositories (both old and new projects)

2. **Repository Permissions:**
   - Ensure "Contents: Read & Write" is enabled
   - This allows the app to read from source and write to destination

---

## Part 3: CI/CD Pipeline Setup (Optional but Recommended)

CI/CD is **not required** for Cursor web agents to work, but it's highly recommended for:

- Automated testing
- Code quality checks
- Deployment automation
- Multi-repo synchronization

### Basic CI/CD Workflow

Create `.github/workflows/ci-cd-pipeline.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r tests/requirements.txt
        
    - name: Run tests
      run: |
        pytest tests/ -v --cov=symphainy_platform --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  lint:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install linting tools
      run: |
        pip install black flake8 mypy
        
    - name: Run Black
      run: black --check .
      
    - name: Run Flake8
      run: flake8 .
      
    - name: Run MyPy
      run: mypy symphainy_platform
```

### Multi-Repo Sync Workflow (For Code Migration)

Create `.github/workflows/sync-from-old-repo.yml`:

```yaml
name: Sync from Old Repository

on:
  workflow_dispatch:  # Manual trigger
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      
    steps:
    - name: Checkout current repo
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Checkout old repo
      uses: actions/checkout@v4
      with:
        repository: YOUR_ORG/old-repo-name
        path: old-repo
        token: ${{ secrets.OLD_REPO_TOKEN }}  # PAT with access to old repo
        
    - name: Sync specific files
      run: |
        # Example: Copy specific files/directories
        cp -r old-repo/specific/path/* symphainy_platform/corresponding/path/
        
    - name: Create Pull Request
      uses: peter-evans/create-pull-request@v5
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        commit-message: "Sync from old repository"
        title: "Sync: Update from old repository"
        body: |
          Automated sync from old repository.
          Review changes carefully before merging.
        branch: sync/from-old-repo
```

**Setup Steps:**

1. **Add Secret for Old Repo Access:**
   - Go to Repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `OLD_REPO_TOKEN`
   - Value: Personal Access Token with access to old repo
   - Click "Add secret"

2. **Update the workflow:**
   - Replace `YOUR_ORG/old-repo-name` with your actual old repo path
   - Customize the sync logic in the "Sync specific files" step

---

## Part 4: Cursor Web Agent Configuration

### Repository-Specific Settings

Create or update `.cursor/web-agent-config.json`:

```json
{
  "github": {
    "repositories": [
      {
        "name": "symphainy-prod",
        "owner": "Aaron-Lilly",
        "path": "symphainy_source_code",
        "default_branch": "main"
      },
      {
        "name": "old-repo-name",
        "owner": "YOUR_ORG",
        "path": ".",
        "default_branch": "main",
        "read_only": true
      }
    ],
    "sync_strategy": "manual",
    "auto_commit": false,
    "create_prs": true
  },
  "code_migration": {
    "enabled": true,
    "source_repos": ["YOUR_ORG/old-repo-name"],
    "target_repo": "Aaron-Lilly/symphainy-prod",
    "mapping_file": ".cursor/migration-mapping.json"
  }
}
```

### Migration Mapping File

Create `.cursor/migration-mapping.json` to guide code migration:

```json
{
  "file_mappings": {
    "old-repo/backend/platform/": "symphainy_source_code/symphainy_platform/",
    "old-repo/tests/": "symphainy_source_code/tests/",
    "old-repo/docs/": "symphainy_source_code/docs/"
  },
  "exclude_patterns": [
    "**/__pycache__/",
    "**/*.pyc",
    "**/.env*",
    "**/node_modules/"
  ],
  "transformations": {
    "import_paths": {
      "from platform.": "from symphainy_platform.",
      "from smart_cities.": "from symphainy_platform.realms."
    }
  }
}
```

---

## Part 5: Testing the Setup

### Test 1: Basic Repository Access

1. Open Cursor
2. Open the repository: `symphainy-prod`
3. Try a simple agent task: "List all Python files in the platform directory"
4. Verify the agent can read the repository

### Test 2: Multi-Repo Access

1. Ask the agent: "Compare the architecture between the old repo and this repo"
2. Verify the agent can access both repositories
3. Check that it can read from the old repo

### Test 3: Code Migration

1. Ask the agent: "Migrate the Session class from the old repo to this repo, adapting it to the new architecture"
2. Verify the agent:
   - Reads from old repo
   - Understands new architecture (from `.cursorrules`)
   - Creates appropriate code in new location
   - Updates imports correctly

---

## Part 6: Security Best Practices

### 1. Token Security

- ✅ Store tokens in Cursor's secure storage (not in code)
- ✅ Use fine-grained tokens with minimal permissions
- ✅ Rotate tokens regularly (every 90 days)
- ✅ Never commit tokens to git

### 2. Repository Access

- ✅ Use "Least Privilege" principle
- ✅ Grant read-only access when possible
- ✅ Use separate tokens for different purposes
- ✅ Monitor token usage in GitHub Settings

### 3. Code Migration Safety

- ✅ Always create PRs (don't push directly to main)
- ✅ Review all migrations before merging
- ✅ Run tests after migration
- ✅ Use staging branches for large migrations

---

## Troubleshooting

### Issue: "Agent cannot access repository"

**Solutions:**
1. Verify token has correct scopes (`repo` scope required)
2. Check repository visibility (private repos need token)
3. Verify token hasn't expired
4. Check repository permissions in GitHub

### Issue: "Agent cannot access multiple repos"

**Solutions:**
1. Ensure token has access to all repos
2. For org repos: verify user is member/collaborator
3. Check GitHub App installation includes all repos
4. Verify repository paths in config are correct

### Issue: "Code migration creates broken imports"

**Solutions:**
1. Update `migration-mapping.json` with correct transformations
2. Review `.cursorrules` for import patterns
3. Run tests after migration
4. Use IDE refactoring tools to fix imports

---

## Next Steps

1. ✅ Set up GitHub token/app
2. ✅ Configure multi-repo access
3. ✅ Create CI/CD workflows (optional)
4. ✅ Test basic agent access
5. ✅ Test code migration
6. ✅ Set up monitoring/alerting for migrations

---

## Additional Resources

- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub Apps](https://docs.github.com/en/apps/creating-github-apps)
- [Cursor Documentation](https://cursor.sh/docs)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Last Updated:** January 2026
