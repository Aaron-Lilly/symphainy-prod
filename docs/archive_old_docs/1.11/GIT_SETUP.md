# Git Setup Instructions

## Initial Repository Setup

### 1. Initialize Git (if not already done)

```bash
cd /home/founders/demoversion/symphainy_source_code
git init
```

### 2. Add Remote Repository

```bash
git remote add origin git@github.com:Aaron-Lilly/symphainy-prod.git
```

### 3. Verify Remote

```bash
git remote -v
# Should show:
# origin  git@github.com:Aaron-Lilly/symphainy-prod.git (fetch)
# origin  git@github.com:Aaron-Lilly/symphainy-prod.git (push)
```

### 4. Create Initial Commit

```bash
# Stage all files
git add .

# Create initial commit
git commit -m "Week 0: Initial scaffold - Platform structure, tests, CI/CD, Cursor config"

# Push to main branch
git branch -M main
git push -u origin main
```

## Environment Secrets Setup

### 1. Copy Environment Template

```bash
cp .env.example .env.secrets
```

### 2. Edit `.env.secrets` with Your Values

**Important:** `.env.secrets` is already in `.gitignore` and will NOT be committed.

### 3. Verify `.env.secrets` is Ignored

```bash
git status
# .env.secrets should NOT appear in the list
```

## Branch Protection (Recommended)

After initial push, consider setting up branch protection in GitHub:

1. Go to repository settings
2. Navigate to "Branches"
3. Add rule for `main` branch:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date

## SSH Key Setup (if needed)

If you haven't set up SSH keys for GitHub:

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub
# Add this to GitHub: Settings > SSH and GPG keys > New SSH key
```

## Verification Checklist

- [ ] Git repository initialized
- [ ] Remote added (git@github.com:Aaron-Lilly/symphainy-prod.git)
- [ ] `.env.secrets` created (not committed)
- [ ] `.gitignore` includes `.env.secrets`
- [ ] Initial commit created
- [ ] Pushed to GitHub
- [ ] SSH access working

## Next Steps

After setup:
1. Continue with Week 1: Runtime Plane v0
2. Commit changes regularly
3. Push to GitHub as needed
