# Execution Documentation - Current vs Historical

**Last Updated:** January 2026  
**Purpose:** Clarify what's current truth vs historical reference

---

## 📋 Current Truth (What Exists Today)

These documents represent the **current state** of the platform:

### API Contracts
- **[API Contracts for Frontend Integration](api_contracts_frontend_integration.md)** ⭐ CURRENT
  - Complete API contracts for all Phase 1-4 intents
  - Request/response formats
  - Error handling patterns
  - **Use this for:** Frontend integration, API reference

### Testing
- **[Comprehensive Testing Plan (Updated)](comprehensive_testing_plan_updated.md)** ⭐ CURRENT
  - Current testing strategy
  - Test coverage status
  - Testing infrastructure
  - **Use this for:** Understanding test strategy, running tests

- **[Test Results Final Analysis](test_results_final_analysis.md)** ⭐ CURRENT
  - Current test status (85% pass rate)
  - Real issues fixed
  - Production readiness assessment
  - **Use this for:** Understanding test status, production readiness

### Implementation Status
- **[Phase 4 Implementation Summary](phase4_implementation_summary.md)** ⭐ CURRENT
  - What's implemented in Content Realm Phases 1-4
  - All intents and capabilities
  - **Use this for:** Understanding what's available today

### Architecture Decisions
- **[WebSocket Agent Endpoint Architecture](websocket_agent_endpoint_architecture.md)** ⭐ CURRENT
  - Current architecture decision for WebSocket endpoints
  - Experience Plane owns `/api/runtime/agent`
  - **Use this for:** Understanding WebSocket architecture

---

## 📚 Historical Reference (How We Got Here)

These documents are **archived for reference** but are not current truth:

### Archived Implementation Records
- `ARCHIVE/phase_0_complete.md` - Historical completion record
- `ARCHIVE/phase_1_complete.md` - Historical completion record
- `ARCHIVE/phase1_validation_results.md` - Historical validation
- `ARCHIVE/phase2_implementation_summary.md` - Historical implementation
- `ARCHIVE/phase3_implementation_summary.md` - Historical implementation

### Archived Gap Analyses
- `ARCHIVE/gap_analysis_*.md` - Historical gap analyses (gaps are now resolved)
- `ARCHIVE/architectural_fixes_analysis.md` - Historical architectural fixes

### Archived Status Documents
- `ARCHIVE/frontend_refactoring_*.md` - Historical refactoring records
- `ARCHIVE/insights_realm_implementation_status.md` - Historical status

---

## 🗑️ Obsolete (Do Not Use)

These documents are **obsolete** and should not be referenced:

- Duplicate testing plans (use `comprehensive_testing_plan_updated.md` only)
- Duplicate status documents (consolidated into current state docs)
- Outdated gap analyses (gaps are resolved)

---

## 🎯 Quick Reference

**Need to know what the platform can do?**
→ See [Platform Overview](../PLATFORM_OVERVIEW.md)

**Need API contracts?**
→ See [API Contracts for Frontend Integration](api_contracts_frontend_integration.md)

**Need to understand test status?**
→ See [Test Results Final Analysis](test_results_final_analysis.md)

**Need implementation details?**
→ See [Phase 4 Implementation Summary](phase4_implementation_summary.md)

**Need architecture decisions?**
→ See [Architecture Guide](../architecture/north_star.md)

---

## 📁 Organization

This folder contains:
- **Current truth** - Documents that represent current state
- **ARCHIVE/** - Historical documents for reference
- **checklists/** - Progress tracking checklists

**Principle:** If a document is not marked as ⭐ CURRENT, assume it's historical reference only.
