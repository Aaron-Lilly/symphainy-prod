# Cursor Web Agents Setup Guide

## Status: 📋 **IMPLEMENTATION GUIDE**

**Date:** January 27, 2026

---

## Executive Summary

This guide outlines what's needed to enable **Cursor Web Agents** to help build the SymphAIny platform. Cursor Web Agents can act as a "compiler backend" that takes semantic build instructions and produces code artifacts, following the pattern outlined in the Agentic IDP vision.

---

## Current Setup Analysis

### What You Have Now
- ✅ **GitHub Repo:** `git@github.com:Aaron-Lilly/symphainy-prod.git`
- ✅ **VM Access:** SSH tunnel from local machine
- ✅ **Codebase:** ~79K lines of Python code
- ✅ **Architecture Documentation:** Comprehensive contracts and architecture docs
- ⚠️ **Repo Status:** Outdated (many uncommitted changes)

### What Cursor Web Agents Need

1. **Access to Codebase**
   - GitHub repo access (read/write)
   - Ability to understand code structure
   - Ability to make changes and see results

2. **Architecture Understanding**
   - Access to contracts (intent, journey, solution)
   - Understanding of artifact-centric patterns
   - Knowledge of realm structure and boundaries

3. **Testing & Validation**
   - Ability to run tests
   - Contract validation
   - See test results

4. **Context & Documentation**
   - Access to architecture docs
   - Understanding of patterns and conventions
   - Knowledge of what's been done vs what needs to be done

---

## Requirements for Cursor Web Agents

### 1. GitHub Repository Setup

#### Current Status
- **Repo:** `git@github.com:Aaron-Lilly/symphainy-prod.git`
- **Status:** Outdated (many uncommitted changes)
- **Access:** SSH-based (git@github.com)

#### What's Needed

**Option A: Sync Current State (Recommended)**
```bash
# 1. Commit current changes
cd /home/founders/demoversion/symphainy_source_code
git add .
git commit -m "WIP: Architectural epiphany - solution contracts and migration strategy"

# 2. Push to GitHub
git push origin main

# 3. Create feature branch for Cursor Web Agents work
git checkout -b cursor-web-agents-setup
git push -u origin cursor-web-agents-setup
```

**Option B: Create Fresh Branch for New Architecture**
```bash
# 1. Create new branch from current state
cd /home/founders/demoversion/symphainy_source_code
git checkout -b symphainy-platform-v2
git add .
git commit -m "Architectural pivot: Solution-centric architecture with contracts"

# 2. Push to GitHub
git push -u origin symphainy-platform-v2
```

**Recommendation:** Option B - Create a new branch for the v2 architecture work. This keeps the main branch stable while allowing Cursor Web Agents to work on the new architecture.

---

### 2. Cursor Web Agents Configuration

#### What Cursor Web Agents Need to Know

**Architecture Context:**
- Solution → Journey → Intent hierarchy
- Artifact-centric patterns
- Realm structure (Content, Insights, Journey, Outcomes)
- Smart City primitives
- Contract-based testing

**Patterns & Conventions:**
- Intent services (SOA APIs)
- Orchestrators in Journey Realm
- Solution contracts at top level
- Coexistence components (GuideAgent + Liaison Agents)

**What to Build:**
- MVP Solution (Security, Coexistence, Control Tower, Platform MVP)
- Intent services extracted from orchestrators
- Journey orchestrators in Journey Realm
- Solution contracts and journey contracts

#### Configuration File

Create `.cursor/agents-config.json`:

```json
{
  "project_name": "SymphAIny Platform v2",
  "architecture": {
    "pattern": "solution_centric",
    "hierarchy": ["solution", "journey", "intent"],
    "realms": ["content", "insights", "journey", "outcomes"],
    "civic_systems": ["smart_city", "agentic", "experience"]
  },
  "contracts": {
    "location": "docs/01242026_final/intent_contracts/",
    "journey_location": "docs/01242026_final/journey_contracts/",
    "solution_location": "docs/01242026_final/solution_contracts/"
  },
  "patterns": {
    "artifact_centric": true,
    "intent_services": true,
    "orchestrators_in_journey_realm": true,
    "solution_contracts": true
  },
  "current_work": {
    "phase": "migration_to_v2",
    "focus": "extract_intent_services",
    "next_steps": [
      "Create intent services from ContentOrchestrator",
      "Move orchestrators to Journey Realm",
      "Define solution contracts",
      "Build journey orchestrators"
    ]
  },
  "constraints": {
    "no_backward_compatibility": true,
    "contract_based_testing": true,
    "artifact_centric_only": true
  }
}
```

---

### 3. Documentation for Cursor Web Agents

#### Essential Documents

Create `.cursor/AGENTS_README.md`:

```markdown
# Cursor Web Agents Guide for SymphAIny Platform

## Architecture Overview

This platform follows a **solution-centric architecture**:

1. **Solutions** compose **Journeys**
2. **Journeys** compose **Intents**
3. **Intents** are **Realm Intent Services** (SOA APIs)

## Key Patterns

### Artifact-Centric
- Everything is an artifact
- Artifacts have lifecycle states (PENDING → READY → ARCHIVED)
- Artifacts have materializations (storage locations)
- Artifacts have lineage (parent_artifacts)

### Intent Services
- Intent services are SOA APIs in realms
- They align to intent contracts
- They return artifacts and events
- They never bypass Runtime

### Orchestrators
- Orchestrators live in Journey Realm
- They compose realm intent services
- They expose as MCP tools for agents
- They use agents when journeys require reasoning

### Solutions
- Solutions are top-level user-facing applications
- They compose journeys
- They have coexistence components (GuideAgent + Liaison Agents)
- They have contracts at solution level

## Current Migration Work

We're migrating from old architecture to new:

**Old:**
- Orchestrators in realms
- File-centric patterns
- Mixed patterns

**New:**
- Orchestrators in Journey Realm
- Artifact-centric patterns
- Solution contracts at top level

## What to Build

1. Extract intent services from orchestrators
2. Move orchestrators to Journey Realm
3. Define solution contracts
4. Build journey orchestrators
5. Create solution registry

## Contract Locations

- Intent Contracts: `docs/01242026_final/intent_contracts/`
- Journey Contracts: `docs/01242026_final/journey_contracts/`
- Solution Contracts: `docs/01242026_final/solution_contracts/`

## Testing

- Contract-based testing required
- All intents must align to contracts
- All journeys must align to contracts
- All solutions must align to contracts
```

---

### 4. GitHub Access Setup

#### For Cursor Web Agents

Cursor Web Agents need GitHub access. Options:

**Option A: GitHub App (Recommended)**
- Create GitHub App with repository access
- Grant read/write permissions
- Use app authentication

**Option B: Personal Access Token**
- Create PAT with repo scope
- Store securely (use GitHub Secrets)
- Use token for authentication

**Option C: SSH Keys (Current Setup)**
- Already configured (git@github.com)
- Cursor Web Agents can use existing SSH setup
- May need to configure SSH agent forwarding

#### Recommended: GitHub App

1. **Create GitHub App:**
   - Go to GitHub Settings → Developer settings → GitHub Apps
   - Create new app
   - Grant repository access
   - Grant permissions: Contents (read/write), Pull requests (read/write), Issues (read/write)

2. **Install App:**
   - Install on repository
   - Grant access to repository

3. **Configure Cursor:**
   - Add GitHub App credentials to Cursor settings
   - Configure repository access

---

### 5. Testing & Validation Setup

#### What's Needed

**Test Infrastructure:**
- Ability to run pytest tests
- Contract validation tests
- Integration tests
- E2E tests

**Validation:**
- Contract compliance checks
- Pattern validation
- Architecture validation

#### Setup

Create `.cursor/test-config.json`:

```json
{
  "test_framework": "pytest",
  "test_location": "tests/",
  "contract_tests": "tests/contracts/",
  "integration_tests": "tests/integration/",
  "e2e_tests": "tests/e2e/",
  "validation": {
    "contract_compliance": true,
    "pattern_validation": true,
    "architecture_validation": true
  }
}
```

---

### 6. Cursor Web Agents Workflow

#### How Cursor Web Agents Will Work

**Pattern: Tool-as-Adapter, Not Brain**

1. **Receive Semantic Instructions:**
   - "Extract intent service `parse_artifact` from ContentOrchestrator"
   - "Create solution contract for Security Solution"
   - "Move orchestrators to Journey Realm"

2. **Understand Context:**
   - Read contracts
   - Understand architecture
   - Know patterns and conventions

3. **Generate Code:**
   - Create intent services
   - Create solution contracts
   - Update orchestrators

4. **Validate:**
   - Run contract tests
   - Validate patterns
   - Check architecture compliance

5. **Create Artifacts:**
   - Code artifacts (source)
   - Test artifacts (validated)
   - Documentation artifacts

#### Example Workflow

```
User: "Extract intent service `parse_artifact` from ContentOrchestrator"

Cursor Web Agent:
1. Reads ContentOrchestrator code
2. Reads parse_content intent contract
3. Extracts parse_artifact logic
4. Creates intent service in Content Realm
5. Updates to artifact-centric patterns
6. Creates tests
7. Validates against contract
8. Creates PR with changes
```

---

## Implementation Steps

### Step 1: Sync Repository (Day 1)

```bash
# 1. Commit current work
cd /home/founders/demoversion/symphainy_source_code
git add .
git commit -m "WIP: Architectural epiphany and migration strategy"

# 2. Create v2 branch
git checkout -b symphainy-platform-v2
git push -u origin symphainy-platform-v2

# 3. Create .cursor directory
mkdir -p .cursor
```

### Step 2: Create Configuration Files (Day 1)

```bash
# 1. Create agents config
cat > .cursor/agents-config.json << 'EOF'
{
  "project_name": "SymphAIny Platform v2",
  "architecture": {
    "pattern": "solution_centric",
    "hierarchy": ["solution", "journey", "intent"],
    "realms": ["content", "insights", "journey", "outcomes"]
  },
  "contracts": {
    "location": "docs/01242026_final/intent_contracts/",
    "journey_location": "docs/01242026_final/journey_contracts/",
    "solution_location": "docs/01242026_final/solution_contracts/"
  }
}
EOF

# 2. Create agents README
# (Copy content from section 3 above)

# 3. Create test config
# (Copy content from section 5 above)
```

### Step 3: Configure GitHub Access (Day 1)

1. **Create GitHub App** (if using Option A)
2. **Install on repository**
3. **Configure Cursor** with app credentials

OR

1. **Create Personal Access Token** (if using Option B)
2. **Store in Cursor settings**
3. **Grant repository access**

### Step 4: Test Cursor Web Agents (Day 2)

1. **Simple Task:**
   - "Create solution contract template"
   - Verify Cursor Web Agent can:
     - Read architecture docs
     - Understand solution contract structure
     - Generate template

2. **Medium Task:**
   - "Extract intent service `ingest_file` from ContentOrchestrator"
   - Verify Cursor Web Agent can:
     - Read ContentOrchestrator code
     - Read intent contract
     - Extract and refactor code
     - Create tests

3. **Complex Task:**
   - "Create Security Solution contract"
   - Verify Cursor Web Agent can:
     - Understand solution architecture
     - Compose journeys
     - Create complete solution contract

### Step 5: Begin Migration Work (Day 3+)

Use Cursor Web Agents to:
1. Extract intent services from orchestrators
2. Create solution contracts
3. Move orchestrators to Journey Realm
4. Build journey orchestrators
5. Create solution registry

---

## Cursor Web Agents Capabilities

### What Cursor Web Agents Can Do

✅ **Code Generation:**
- Create intent services from orchestrators
- Generate solution contracts
- Create journey orchestrators
- Generate tests

✅ **Code Refactoring:**
- Extract intent services
- Move orchestrators
- Update to artifact-centric patterns
- Remove backward compatibility

✅ **Documentation:**
- Generate solution contracts
- Create journey contracts
- Update architecture docs

✅ **Testing:**
- Generate contract tests
- Create integration tests
- Validate patterns

### What Cursor Web Agents Cannot Do (Yet)

❌ **Architectural Decisions:**
- Cannot make architectural decisions
- Cannot decide on patterns
- Cannot determine solution composition

❌ **Business Logic:**
- Cannot implement complex business logic
- Cannot reason about domain logic
- Cannot make judgment calls

❌ **Validation:**
- Cannot validate business requirements
- Cannot approve changes
- Cannot make final decisions

**Note:** Cursor Web Agents are a "compiler backend" - they execute semantic instructions but don't make architectural decisions.

---

## Best Practices

### 1. Clear Instructions

**Good:**
- "Extract intent service `parse_artifact` from ContentOrchestrator, align to contract `parse_content.md`, use artifact-centric patterns"

**Bad:**
- "Refactor ContentOrchestrator"

### 2. Incremental Tasks

**Good:**
- Break large tasks into small, testable pieces
- "Extract intent service X"
- "Create solution contract Y"
- "Move orchestrator Z"

**Bad:**
- "Refactor entire platform"

### 3. Validation

**Good:**
- Always validate against contracts
- Run tests after changes
- Check architecture compliance

**Bad:**
- Make changes without validation

### 4. Documentation

**Good:**
- Update contracts when making changes
- Document architectural decisions
- Keep README updated

**Bad:**
- Make changes without documentation

---

## Troubleshooting

### Issue: Cursor Web Agents Can't Access GitHub

**Solution:**
- Check GitHub access configuration
- Verify SSH keys or tokens
- Test repository access manually

### Issue: Cursor Web Agents Don't Understand Architecture

**Solution:**
- Improve `.cursor/AGENTS_README.md`
- Add more examples
- Clarify patterns and conventions

### Issue: Generated Code Doesn't Match Patterns

**Solution:**
- Provide more specific instructions
- Include examples in instructions
- Validate and correct generated code

### Issue: Tests Fail After Changes

**Solution:**
- Run tests before committing
- Fix issues incrementally
- Validate against contracts

---

## Success Criteria

### Technical Success
- [ ] Cursor Web Agents can access GitHub repo
- [ ] Cursor Web Agents can read and understand contracts
- [ ] Cursor Web Agents can generate code following patterns
- [ ] Cursor Web Agents can create tests
- [ ] Cursor Web Agents can validate against contracts

### Business Success
- [ ] Cursor Web Agents accelerate development
- [ ] Generated code aligns to architecture
- [ ] Contract compliance maintained
- [ ] Migration progress faster with Cursor Web Agents

---

## Next Steps

1. **Sync Repository:** Commit current work and create v2 branch
2. **Create Configuration:** Set up `.cursor/` directory with config files
3. **Configure GitHub Access:** Set up GitHub App or PAT
4. **Test Cursor Web Agents:** Start with simple tasks
5. **Begin Migration:** Use Cursor Web Agents for migration work

---

## Conclusion

Cursor Web Agents can significantly accelerate the migration to v2 architecture by:
- Extracting intent services from orchestrators
- Creating solution contracts
- Generating tests
- Validating against contracts

**Key Insight:** Cursor Web Agents are a "compiler backend" - they execute semantic instructions but don't make architectural decisions. You provide the architecture, they generate the code.

---

**Last Updated:** January 27, 2026  
**Owner:** Development Team
