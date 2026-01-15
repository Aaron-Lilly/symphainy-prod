# Symphainy Platform - Development Guide

**Last Updated:** January 2026  
**Status:** Active Development - Platform Rebuild  
**Version:** 2.0 (Breaking Changes - No Backwards Compatibility)

---

## 🎯 Quick Navigation

- **Architecture:** [docs/architecture/north_star.md](architecture/north_star.md) - The authoritative architectural guide
- **Platform Rules:** [docs/PLATFORM_RULES.md](PLATFORM_RULES.md) - Rules of the road for development
- **Current State:** [docs/current_state/00_CURRENT_STATE_INDEX.md](current_state/00_CURRENT_STATE_INDEX.md) - What exists, what's missing
- **Roadmap:** [docs/roadmap/00_ROADMAP_INDEX.md](roadmap/00_ROADMAP_INDEX.md) - High-level roadmap
- **Execution Plan:** [docs/execution/00_EXECUTION_INDEX.md](execution/00_EXECUTION_INDEX.md) - Detailed implementation plans

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

## 📋 Current Phase

**Phase 0: Foundation & Assessment** (Week 1)
- Archive current implementations
- Audit Public Works
- Establish baseline

**Next:** Phase 1: Tech Stack Evolution (Week 2-3)

See [execution/00_EXECUTION_INDEX.md](execution/00_EXECUTION_INDEX.md) for detailed plans.

---

## 📚 Document Structure

```
docs/
├── 00_START_HERE.md              # This file - entry point
├── PLATFORM_RULES.md             # Development rules and standards
├── architecture/
│   ├── north_star.md             # Authoritative architecture guide
│   ├── patterns/                 # Pattern documentation
│   └── decisions/                # Architecture Decision Records
├── current_state/                # Current platform state
├── roadmap/                      # High-level roadmap
└── execution/                    # Detailed implementation plans
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

- [Architecture Guide](architecture/north_star.md)
- [Platform Rules](PLATFORM_RULES.md)
- [Execution Plans](execution/00_EXECUTION_INDEX.md)
- [Use Cases](platform_use_cases/)

---

**Remember:** We're building a platform that works. No shortcuts. No cheats. No backwards compatibility baggage.
