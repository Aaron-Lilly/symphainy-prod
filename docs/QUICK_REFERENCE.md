# Quick Reference Guide

**For:** Developers using Cursor to build the platform  
**Last Updated:** January 2026

---

## 🚀 Getting Started

1. **Read:** [00_START_HERE.md](00_START_HERE.md)
2. **Read:** [PLATFORM_RULES.md](PLATFORM_RULES.md)
3. **Read:** [Architecture Guide](architecture/north_star.md)
4. **Check:** [Current State](current_state/00_CURRENT_STATE_INDEX.md)
5. **Execute:** [Phase 0 Execution Plan](execution/phase_0_execution_plan.md)

---

## 🎯 Critical Rules (Remember These)

1. **No Backwards Compatibility** - This is v2.0. Breaking changes only.
2. **No Stubs/Cheats** - All code must work. No `pass`, `# TODO`, placeholders.
3. **Tests Must Fail with Cheats** - If code has stubs, tests must fail.
4. **Public Works First** - All infrastructure via Public Works abstractions.
5. **Architecture Guide Wins** - Code must match architecture guide.

---

## 📁 Document Structure

```
docs/
├── 00_START_HERE.md              # Entry point
├── PLATFORM_RULES.md             # Development rules
├── QUICK_REFERENCE.md            # This file
├── architecture/
│   ├── north_star.md             # Architecture guide
│   ├── patterns/                 # Pattern docs
│   └── decisions/                # ADRs
├── current_state/                # Current state docs
├── roadmap/                      # High-level roadmap
└── execution/                    # Detailed plans
    └── checklists/               # Progress tracking
```

---

## 🏗️ Architecture Quick Reference

### Four Classes of Things

1. **Runtime** - Execution authority (owns execution and state)
2. **Civic Systems** - Governance (Smart City, Experience, Agentic, Platform SDK)
3. **Domain Services** - Domain logic (Content, Insights, Operations, Outcomes)
4. **Foundations** - Infrastructure (Public Works)

### Runtime Participation Contract

```python
handle_intent(intent, runtime_context) → { artifacts, events }
```

### Public Works Pattern

```
Protocol (Contract) → Abstraction (Business Logic) → Adapter (Technology)
```

---

## 🔧 Common Tasks

### Adding Infrastructure

1. Create adapter in `foundations/public_works/adapters/`
2. Create abstraction in `foundations/public_works/abstractions/`
3. Create protocol in `foundations/public_works/protocols/`
4. Register in `foundations/public_works/foundation_service.py`
5. Write tests (must fail if adapter has stubs)

### Adding Domain Service

1. Create service in `realms/{realm_name}/`
2. Implement Runtime Participation Contract
3. Use Public Works abstractions
4. Register with Curator
5. Write tests (must fail if service has stubs)

### Migrating Infrastructure

1. Create new adapter (Layer 0)
2. Update abstraction to use new adapter (Layer 1)
3. Update foundation service (Layer 4)
4. Verify business logic unchanged (validates pattern)

---

## ✅ Checklist for Every Change

- [ ] Code works (no stubs/cheats)
- [ ] Tests pass (and would fail if code had cheats)
- [ ] Uses Public Works abstractions
- [ ] Matches architecture guide
- [ ] Has type hints
- [ ] Has docstrings
- [ ] Handles errors properly
- [ ] No backwards compatibility code
- [ ] Documented in execution checklist

---

## 📚 Key Documents

- [Architecture Guide](architecture/north_star.md) - Source of truth
- [Platform Rules](PLATFORM_RULES.md) - Development standards
- [Execution Plans](execution/00_EXECUTION_INDEX.md) - Detailed plans
- [Roadmap](roadmap/00_ROADMAP_INDEX.md) - High-level roadmap

---

## 🆘 Need Help?

1. **Architecture Question?** → Read [north_star.md](architecture/north_star.md)
2. **Development Question?** → Read [PLATFORM_RULES.md](PLATFORM_RULES.md)
3. **Implementation Question?** → Read [execution plans](execution/00_EXECUTION_INDEX.md)
4. **Pattern Question?** → Read [patterns](architecture/patterns/)

---

**Remember:** Working code only. No shortcuts. No cheats.
