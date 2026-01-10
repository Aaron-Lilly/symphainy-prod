# Repository Cleanup Plan

**Issue:** The `symphainy-prod` repository contains the entire old repository instead of being a clean new build.

**Root Cause:** When we removed secrets using `git filter-branch`, we rewrote the old repo's entire history and pushed it as the "new" repo.

---

## What Happened

1. We used `git filter-branch` to remove secret files from the old repo
2. This rewrote the entire git history (all 4,316 files)
3. We then pushed this as the "new" `symphainy-prod` repo
4. Result: The new repo contains ALL the old repo's content

---

## What Should Be in the New Repo

### ✅ KEEP (New Clean Structure):
- `symphainy_platform/` - New clean platform structure
- `tests/` - Test suite
- `docs/` - Documentation
- `config/` - Configuration files
- `scripts/` - Utility scripts
- `symphainy-frontend/` - Frontend (if needed)
- Basic files: README.md, .gitignore, .cursorrules, etc.

### ❌ REMOVE (Old Repo Content):
- `agentic/` - Old agentic structure
- `archived_foundations/` - Old archived code
- `backend/` - Old backend structure
- `symphainy-mvp-*` - Old MVP versions
- `symphainy_source/` - The old repo itself!
- `symphainy-platform/` - Old platform structure (different from `symphainy_platform/`)
- `oct7cleanup/`, `recovery/`, `z_docs/` - Old cleanup/recovery directories
- Any other old directories

---

## Cleanup Options

### Option 1: Clean Slate (Recommended)
Create a completely new initial commit with only the clean structure:

1. Create a new orphan branch
2. Add only the files that should be in the new repo
3. Force push to replace the current history

### Option 2: Remove Old Directories
Keep the current history but remove all old directories:

1. Remove old directories from git
2. Commit the cleanup
3. Push to GitHub

### Option 3: Start Fresh Repository
Create a brand new GitHub repository and push only the clean structure.

---

## Recommendation

**Option 1 (Clean Slate)** is recommended because:
- The current history contains 4,316 files from the old repo
- Starting fresh gives you a clean git history
- Easier to maintain going forward
- No confusion about what's old vs new

---

## Next Steps

1. Decide which cleanup option you prefer
2. I'll help you execute the cleanup
3. Verify the repo only contains the new clean structure
4. Update documentation if needed
