# Symphainy Platform - Development Guide

**Last Updated:** January 2026  
**Status:** Active Development - Platform Rebuild  
**Version:** 2.0 (Breaking Changes - No Backwards Compatibility)

---

## 🎯 Quick Navigation

- **Platform Overview:** [docs/PLATFORM_OVERVIEW.md](PLATFORM_OVERVIEW.md) - Executive overview of what the platform does
- **Architecture:** [docs/architecture/north_star.md](architecture/north_star.md) - The authoritative architectural guide
- **Platform Rules:** [docs/PLATFORM_RULES.md](PLATFORM_RULES.md) - Rules of the road for development
- **Current State:** [docs/current_state/00_CURRENT_STATE_INDEX.md](current_state/00_CURRENT_STATE_INDEX.md) - What exists, what's missing
- **Roadmap:** [docs/roadmap/00_ROADMAP_INDEX.md](roadmap/00_ROADMAP_INDEX.md) - High-level roadmap
- **Execution Docs:** [docs/execution/README.md](execution/README.md) - Current implementation documentation

---

## 🚀 Development Workflow

### Starting a Task

1. **Read Architecture:** Review [north_star.md](architecture/north_star.md) for architectural principles
2. **Check Platform Rules:** Review [PLATFORM_RULES.md](PLATFORM_RULES.md) for development standards
3. **Review Current State:** Check [current_state/](current_state/) to understand what exists
4. **Review Roadmap:** Check [roadmap/](roadmap/) to see where we're going
5. **Execute from Plan:** Follow detailed plans in [execution/](execution/)

### Making Decisions

- **Architecture Decisions:** Document in `architecture/decisions/ADR_*.md`
- **Pattern Usage:** Reference `architecture/patterns/*.md`
- **Breaking Changes:** Document in `architecture/decisions/` (we're doing breaking changes, but document why)

### Completing Work

- Update checklists in `execution/checklists/`
- Update current state documentation
- Add tests (no tests pass with cheats/stubs)
- Document any new patterns or decisions

---

## 🎯 Key Principles

### Platform Philosophy

> **Symphainy is a governed execution platform.**
> It runs **Solutions** safely — and those Solutions safely operate, connect to, and reason over external systems.

### Development Philosophy

1. **Breaking Changes Only:** No backwards compatibility. This is a new platform.
2. **Working Code Only:** No stubs, placeholders, or hard-coded cheats unless deliberate and resolved in the same sprint.
3. **Tests Must Pass:** No test can pass if there are any "cheats" in the code.
4. **Public Works Pattern:** All infrastructure via Public Works abstractions (swappable).
5. **Architecture Guide Wins:** If code conflicts with architecture guide, architecture guide is correct.

---

## 📋 Current Status

### ✅ Operational Capabilities

**Content Realm (Complete)**
- File ingestion (upload, EDI, API)
- File parsing (PDF, Excel, binary, images, BPMN, DOCX)
- File management (retrieve, list, metadata)
- Bulk operations (ingestion, parsing, embedding extraction)
- File lifecycle (archive, restore, purge)
- File validation and search

**Insights Realm (Complete)**
- Data quality assessment
- Semantic interpretation
- Interactive analysis (structured and unstructured)
- Guided discovery
- Lineage tracking

**Journey Realm (Complete)**
- Workflow creation from BPMN
- SOP generation from interactive chat
- Visual workflow generation
- Coexistence analysis

**Infrastructure (Complete)**
- Multi-tenant data isolation
- File storage (GCS integration)
- State management (Redis/ArangoDB)
- Graph database (ArangoDB)
- Search engine (Meilisearch)

### 🚧 In Progress
- Frontend integration testing
- Remaining realm implementations
- Production hardening (monitoring, alerting)
- Documentation consolidation

### 📊 Test Status
- **85% test pass rate** (22/26 tests)
- **100% integration test pass rate** (8/8)
- **100% E2E test pass rate** (3/3)

See [execution/README.md](execution/README.md) for current implementation documentation.

---

## 📚 Document Structure

```
docs/
├── 00_START_HERE.md              # This file - developer entry point
├── PLATFORM_OVERVIEW.md          # Executive overview (what platform does)
├── PLATFORM_RULES.md             # Development rules and standards
├── QUICK_REFERENCE.md            # Quick reference guide
├── architecture/
│   ├── north_star.md             # Authoritative architecture guide
│   ├── patterns/                 # Pattern documentation
│   └── decisions/                # Architecture Decision Records
├── capabilities/                 # Platform capabilities (coming soon)
├── current_state/                # Current platform state
├── roadmap/                      # High-level roadmap
└── execution/                    # Implementation documentation
    ├── README.md                 # Current vs historical docs
    ├── ARCHIVE/                  # Historical reference docs
    └── checklists/               # Progress tracking
```

---

## ⚠️ Critical Rules

1. **No Backwards Compatibility:** This is a new platform. Breaking changes are expected.
2. **No Stubs/Cheats:** All code must work. No placeholders unless deliberate and resolved in same sprint.
3. **Tests Must Be Real:** No test can pass if code has cheats.
4. **Public Works First:** All infrastructure via Public Works abstractions.
5. **Architecture Guide Wins:** Code must match architecture guide.

---

## 🔗 Quick Links

- [Platform Overview](PLATFORM_OVERVIEW.md) - What the platform does
- [Architecture Guide](architecture/north_star.md) - How it's built
- [Platform Rules](PLATFORM_RULES.md) - Development standards
- [Execution Documentation](execution/README.md) - Current implementation docs
- [API Contracts](execution/api_contracts_frontend_integration.md) - Frontend integration
- [Use Cases](platform_use_cases/) - Business scenarios

---

**Remember:** We're building a platform that works. No shortcuts. No cheats. No backwards compatibility baggage.
