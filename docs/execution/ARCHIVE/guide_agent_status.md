# Guide Agent Status & Implementation Plan

**Status:** ❌ Missing - Needs Implementation  
**Date:** January 2026  
**Priority:** High (Required for MVP Showcase)

---

## Current Status

### ✅ Pillar Liaison Agents (Complete)

**Insights Liaison Agent:**
- ✅ `symphainy_platform/realms/insights/agents/insights_liaison_agent.py`
- ✅ Handles deep dive analysis for Insights pillar
- ✅ Interactive analysis sessions
- ✅ Question answering, relationship exploration

**Journey Liaison Agent:**
- ✅ `symphainy_platform/realms/journey/agents/journey_liaison_agent.py`
- ✅ Handles SOP generation via chat for Journey/Operations pillar
- ✅ Interactive SOP building

### ❌ Guide Agent (Global Concierge) - Missing

**Status:** Not implemented in current codebase

**Found in Legacy:**
- `symphainy_source/symphainy-platform/foundations/experience_foundation/services/frontend_gateway_service/frontend_gateway_service.py`
  - Has Guide Agent routes and implementation
  - `handle_guide_chat_request()` method
  - Routes for intent analysis, journey guidance, conversation history

**Current Codebase:**
- ❌ No Guide Agent implementation
- ❌ No global concierge service
- ❌ No user navigation guidance

---

## MVP Showcase Requirement

From `mvp_showcase_description.md`:

> "we also have a two part chat interface (guide agent - global concierge and pillar liaison agents (one per pillar) - handles pillar specific interactions (deep dives on analysis with the insights pillar, generating SOPs in the operations pillar, etc.))"

**Required:**
- ✅ Pillar Liaison Agents (2/4 complete - Insights, Journey)
- ❌ Guide Agent (Global Concierge) - **MISSING**

---

## What Guide Agent Should Do

### Core Responsibilities

1. **Platform Navigation**
   - Help users understand what each pillar does
   - Guide users to the right pillar for their needs
   - Explain platform capabilities

2. **User Intent Analysis**
   - Understand what user wants to accomplish
   - Analyze user's goals and requirements
   - Provide contextual recommendations

3. **Journey Guidance**
   - Recommend next steps based on user's current state
   - Suggest which pillar to visit next
   - Guide through complete platform journey

4. **Pillar Routing**
   - Route users to appropriate pillar liaison agents
   - Hand off to pillar-specific agents when needed
   - Coordinate between pillars

5. **User Onboarding**
   - Help first-time users get started
   - Explain platform features
   - Guide through initial setup

6. **Solution Context**
   - Help users define their solution context (from landing page)
   - Understand what they want to accomplish
   - Recommend starting points

---

## Implementation Plan

### Phase 1: Guide Agent Core (Agentic SDK)

**File:** `symphainy_platform/civic_systems/agentic/agents/guide_agent.py`

**Capabilities:**
- Platform navigation guidance
- User intent analysis
- Pillar recommendation
- Solution context understanding
- User journey tracking

**Methods:**
- `analyze_user_intent(message, context)` - Understand what user wants
- `get_journey_guidance(user_state, context)` - Recommend next pillar/action
- `process_chat_message(message, session_id, context)` - Handle user messages
- `route_to_pillar(pillar_name, user_intent, context)` - Route to pillar liaison agent

### Phase 2: Guide Agent Service (Experience Service)

**File:** `symphainy_platform/civic_systems/experience/services/guide_agent_service.py`

**Methods:**
- `analyze_user_intent()` - Analyze user intent
- `get_journey_guidance()` - Get journey guidance
- `get_conversation_history()` - Retrieve chat history
- `process_chat_message()` - Handle user messages
- `route_to_pillar_liaison()` - Route to pillar liaison agent

### Phase 3: Experience Service Integration

**File:** `symphainy_platform/civic_systems/experience/experience_service.py`

**API Endpoints:**
- `POST /api/v1/guide-agent/chat` - Chat with guide agent
- `POST /api/v1/guide-agent/analyze-intent` - Analyze user intent
- `GET /api/v1/guide-agent/guidance` - Get journey guidance
- `GET /api/v1/guide-agent/history/{session_id}` - Get conversation history
- `POST /api/v1/guide-agent/route-to-pillar` - Route to pillar liaison agent

**File:** `symphainy_platform/civic_systems/experience/api/guide_agent.py` (new)

### Phase 4: Integration with Pillar Liaison Agents

- Guide Agent hands off to:
  - Insights Liaison Agent (for deep dive analysis)
  - Journey Liaison Agent (for SOP generation)
  - Content Realm (for file upload guidance)
  - Outcomes Realm (for solution creation guidance)

---

## Architecture

```
Frontend (symphainy-frontend)
  ↓
Experience Service API
  ↓
Guide Agent Service
  ↓
Guide Agent (Agentic SDK)
  ├─→ Insights Liaison Agent (deep dive)
  ├─→ Journey Liaison Agent (SOP generation)
  ├─→ Content Realm (file upload)
  └─→ Outcomes Realm (solution creation)
```

---

## Key Features

### 1. Intent Analysis
- Understand user's goals
- Determine which pillar is most relevant
- Provide contextual recommendations

### 2. Journey Tracking
- Track user's progress through platform
- Understand what they've done
- Recommend next steps

### 3. Pillar Routing
- Route to appropriate pillar liaison agents
- Coordinate between pillars
- Maintain context across pillars

### 4. Solution Context
- Help users define their solution context
- Understand their goals upfront
- Guide them through the platform journey

---

## Files to Create

1. `symphainy_platform/civic_systems/agentic/agents/guide_agent.py`
2. `symphainy_platform/civic_systems/experience/services/guide_agent_service.py`
3. `symphainy_platform/civic_systems/experience/api/guide_agent.py`

## Files to Modify

1. `symphainy_platform/civic_systems/experience/experience_service.py`
   - Add Guide Agent Service
   - Include Guide Agent router

2. `symphainy_platform/civic_systems/agentic/agents/__init__.py`
   - Export GuideAgent

---

## Next Steps

1. **Review Legacy Implementation** - Check `symphainy_source` for Guide Agent patterns
2. **Design Guide Agent** - Define capabilities and integration points
3. **Implement Guide Agent Core** - Create agent in Agentic SDK
4. **Create Guide Agent Service** - API layer in Experience Service
5. **Integrate with Experience Service** - Add API endpoints
6. **Test Integration** - Verify Guide Agent works with frontend

---

## Priority

**High** - Required for MVP Showcase. Guide Agent is the primary user interface for navigation and onboarding.
