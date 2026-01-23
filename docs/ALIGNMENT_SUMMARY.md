# Admin Dashboard & Agentic IDP Alignment Summary

**Date:** January 2026  
**Status:** ✅ **FULLY ALIGNED**

---

## Executive Summary

We've aligned on the strategic vision for evolving the Admin Dashboard to support Agentic IDP (SDLC Journey) capabilities, with a critical bridge between Business User outcomes and SDLC execution.

---

## Key Decisions Made

### 1. UI Structure
✅ **Evolve Developer View → SDLC Journey View**
- Keep existing docs/examples as "Reference" tab
- Add "SDLC Journey" tab as primary interface
- Maintain 3-view structure (Control Room, SDLC Journey, Business User)

### 2. Journey Types
✅ **Show all 4 types, prioritize by client demand**
- Modernize, Build, Extend, Replatform
- All visible in UI, prioritize based on what clients pay for

### 3. Metrics Architecture
✅ **Separate SDLC PMO Hub + Control Room Summary**
- SDLC PMO Hub: Dedicated dashboard for SDLC journey metrics
- Control Room: Gets summary SDLC metrics for holistic platform view
- Integration: SDLC PMO Hub exposes summary API → Control Room consumes

### 4. Realm Agent Participation
✅ **Governed participation via SDLC Orchestrators**
- SDLC Orchestrators call Realm Orchestrators (via Runtime)
- Both SDLC journey policy AND realm policy must be satisfied
- Full audit trail for cross-realm participation

### 5. Business User Integration
✅ **Explicit "Launch Journey" button**
- Business User View: "Implementation Preparation" workflow
- Guided configuration (business-friendly language)
- Generates SDLC Journey Configuration
- Explicit [Launch SDLC Journey] action

### 6. Frontend Priority
✅ **UI vision first, then backend, then frontend**
- Phase 0: Align on UI vision (mockups/wireframes)
- Phase 1-2: Build backend
- Phase 3-4: Build frontend

---

## Business User → SDLC Handoff Vision

**The Bridge:** After MVP journey completion, Business User View creates everything needed to handoff to SDLC execution.

**Flow:**
```
MVP Journey → Roadmap + POC Proposal Artifacts
  ↓
Business User View: "Implementation Preparation"
  ↓
Guided 6-Step Configuration:
  1. Journey Type Selection
  2. Intent Composition vs. Creation
  3. Artifact Definition
  4. Governance & Promotion
  5. Agent Team Configuration
  6. Review & Launch
  ↓
SDLC Journey Configuration
  ↓
[Launch SDLC Journey] → SDLC Journey View
```

**Starting Point:** POC Proposal (easier to scope than full Roadmap)

**See:** `BUSINESS_USER_SDLC_HANDOFF_VISION.md` for full details

---

## Implementation Phases

### Phase 0: UI Vision Alignment (1 week)
- Design all three views (SDLC Journey, Business User, SDLC PMO Hub)
- Create mockups/wireframes
- Get stakeholder approval

### Phase 1: Foundation (2-3 weeks)
- Create SDLC Journey Service
- Add SDLC journey APIs
- Create journey data models
- Integrate Metrics API (summary to Control Room)
- Create SDLC PMO Hub service skeleton

### Phase 2: Journey Orchestration (3-4 weeks)
- Implement 7-phase journey flow
- Agent team coordination
- Artifact lifecycle
- Realm agent participation (governed)

### Phase 3: Business User Handoff (2-3 weeks)
- Implementation Preparation Service
- POC Proposal parser
- Guided configuration workflow
- Build UI

### Phase 4: UI Implementation (4-5 weeks)
- SDLC Journey View (7-phase flow)
- SDLC PMO Hub (metrics dashboard)
- Integration with backend

### Phase 5: Cursor/Codex Integration (2-3 weeks)
- Code generation adapters
- Integration into Builder agent

### Phase 6: Self-Hosting (2-3 weeks)
- Dogfood SDLC Journey
- Platform evolution via SDLC Journey

---

## Key Documents

1. **ADMIN_DASHBOARD_AGENTIC_IDP_ALIGNMENT.md** - Strategic alignment
2. **BUSINESS_USER_SDLC_HANDOFF_VISION.md** - Business → SDLC handoff details
3. **This document** - Summary of alignment

---

## Next Steps

1. **Create UI vision documents** - Mockups/wireframes for all three views
2. **Define journey data models** - Journey, Phase, Artifact, AgentTeam
3. **Start Phase 0** - UI vision alignment

---

**Status:** ✅ Ready to proceed with Phase 0 (UI Vision Alignment)
