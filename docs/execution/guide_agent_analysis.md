# Guide Agent Analysis

**Status:** Analysis  
**Date:** January 2026  
**Goal:** Determine if Guide Agent (global concierge) exists and what needs to be implemented

---

## MVP Showcase Requirement

From `mvp_showcase_description.md`:

> "we also have a two part chat interface (guide agent - global concierge and pillar liaison agents (one per pillar) - handles pillar specific interactions (deep dives on analysis with the insights pillar, generating SOPs in the operations pillar, etc.))"

**Required Components:**
1. **Guide Agent** - Global concierge (helps users navigate the platform)
2. **Pillar Liaison Agents** - One per pillar (handles pillar-specific interactions)

---

## Current Status

### Pillar Liaison Agents ✅

**Existing:**
- ✅ **Insights Liaison Agent** (`insights_liaison_agent.py`)
  - Handles deep dive analysis for Insights pillar
  - Interactive analysis sessions
  - Question answering, relationship exploration, pattern identification

- ✅ **Journey Liaison Agent** (`journey_liaison_agent.py`)
  - Handles SOP generation via chat for Journey/Operations pillar
  - Interactive SOP building
  - Chat-based workflow creation

**Missing:**
- ⏳ **Content Liaison Agent** (if needed for Content pillar)
- ⏳ **Outcomes Liaison Agent** (if needed for Outcomes pillar)

### Guide Agent (Global Concierge) ❌

**Status:** Not Found in Current Codebase

**Found in Legacy:**
- `symphainy_source/symphainy-platform/foundations/experience_foundation/services/frontend_gateway_service/frontend_gateway_service.py`
  - Has routes for Guide Agent:
    - `/api/v1/journey/guide-agent/analyze-user-intent`
    - `/api/v1/journey/guide-agent/get-journey-guidance`
    - `/api/v1/journey/guide-agent/get-conversation-history/{session_id}`
  - Has `handle_guide_chat_request` method

**Current Codebase:**
- ❌ No Guide Agent found
- ❌ No global concierge implementation
- ❌ No user navigation guidance agent

---

## What Guide Agent Should Do

### Core Responsibilities

1. **Platform Navigation**
   - Help users understand what each pillar does
   - Guide users to the right pillar for their needs
   - Explain platform capabilities

2. **Context Understanding**
   - Understand user's goals and requirements
   - Track user's journey through the platform
   - Provide contextual recommendations

3. **Pillar Routing**
   - Route users to appropriate pillar liaison agents
   - Hand off to pillar-specific agents when needed
   - Coordinate between pillars

4. **User Onboarding**
   - Help first-time users get started
   - Explain platform features
   - Guide through initial setup

5. **Solution Context**
   - Help users define their solution context
   - Understand what they want to accomplish
   - Recommend starting points

---

## Implementation Approach

### Option 1: Create Guide Agent in Agentic SDK
- Location: `symphainy_platform/civic_systems/agentic/agents/guide_agent.py`
- Extends: `ConversationalAgentBase`
- State Awareness: "full" (needs to track user journey)

### Option 2: Create Guide Agent in Experience Service
- Location: `symphainy_platform/civic_systems/experience/services/guide_agent_service.py`
- Integrates with Experience Service
- Provides API endpoints for frontend

### Option 3: Hybrid Approach (Recommended)
- Guide Agent in Agentic SDK (core logic)
- Guide Agent Service in Experience Service (API layer)
- Integration with Experience Service for frontend access

---

## Required Implementation

### 1. Guide Agent (Core)
- **File:** `symphainy_platform/civic_systems/agentic/agents/guide_agent.py`
- **Capabilities:**
  - Platform navigation guidance
  - User intent analysis
  - Pillar recommendation
  - Solution context understanding
  - User journey tracking

### 2. Guide Agent Service (API Layer)
- **File:** `symphainy_platform/civic_systems/experience/services/guide_agent_service.py`
- **Methods:**
  - `analyze_user_intent()` - Understand what user wants
  - `get_journey_guidance()` - Recommend next pillar/action
  - `get_conversation_history()` - Retrieve chat history
  - `process_chat_message()` - Handle user messages

### 3. Experience Service Integration
- **File:** `symphainy_platform/civic_systems/experience/experience_service.py`
- **API Endpoints:**
  - `POST /api/v1/guide-agent/chat` - Chat with guide agent
  - `POST /api/v1/guide-agent/analyze-intent` - Analyze user intent
  - `GET /api/v1/guide-agent/guidance` - Get journey guidance
  - `GET /api/v1/guide-agent/history/{session_id}` - Get conversation history

### 4. Pillar Routing
- Guide Agent should be able to:
  - Route to Insights Liaison Agent (for deep dive analysis)
  - Route to Journey Liaison Agent (for SOP generation)
  - Route to Content Realm (for file upload guidance)
  - Route to Outcomes Realm (for solution creation guidance)

---

## Integration Points

### With Pillar Liaison Agents
- Guide Agent hands off to pillar liaison agents when pillar-specific help is needed
- Guide Agent coordinates between pillars
- Guide Agent tracks overall user journey

### With Experience Service
- Guide Agent accessible via Experience Service API
- Frontend can chat with Guide Agent
- Guide Agent provides navigation recommendations

### With State Surface
- Guide Agent tracks user journey in State Surface
- Stores conversation history
- Maintains user context and goals

---

## Next Steps

1. **Review Legacy Implementation** - Check `symphainy_source` for Guide Agent patterns
2. **Design Guide Agent** - Define capabilities and integration points
3. **Implement Guide Agent** - Create core agent in Agentic SDK
4. **Create Guide Agent Service** - API layer in Experience Service
5. **Integrate with Experience Service** - Add API endpoints
6. **Test Integration** - Verify Guide Agent works with frontend

---

## Questions

1. Should Guide Agent be in Agentic SDK or Experience Service?
2. What level of state awareness does Guide Agent need?
3. How should Guide Agent coordinate with pillar liaison agents?
4. Should Guide Agent have access to realm capabilities for recommendations?
