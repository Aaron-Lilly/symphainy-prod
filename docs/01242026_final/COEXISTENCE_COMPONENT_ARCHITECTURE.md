# Coexistence Component Architecture

## Status: 📋 **ARCHITECTURAL RECOMMENDATION**

**Date:** January 27, 2026

---

## Executive Summary

**Every solution has a coexistence component** - the interface through which humans interact with the platform.

**GuideAgent** is the platform-level concierge that routes to solution-specific **liaison agents**, which provide conversational interfaces for each solution.

**Landing Page** introduces the coexistence concept and GuideAgent as the primary medium for human-platform interaction.

This creates a **consistent, scalable pattern** for human interaction across all solutions.

---

## 1. The Coexistence Component Concept

### What is Coexistence?

**Coexistence** = The interface through which humans interact with the platform.

Every solution needs a way for humans to:
- Understand what the solution does
- Navigate the solution's capabilities
- Get help and guidance
- Interact conversationally

### The Pattern

```
Solution
├── Business Logic (Journeys → Intents)
├── UI Components (React, Next.js)
└── Coexistence Component (GuideAgent + Liaison Agents)
    ├── GuideAgent (Platform-level concierge)
    └── Solution-Specific Liaison Agents (Solution-level conversational interface)
```

---

## 2. Current Architecture Analysis

### What We Have Now

**GuideAgent** (Platform-level):
- Location: `civic_systems/agentic/agents/guide_agent.py`
- Role: Global concierge for platform navigation
- Capabilities:
  - Platform navigation guidance
  - User intent analysis
  - Pillar recommendation
  - Routing to pillar liaison agents

**Liaison Agents** (Realm/Solution-level):
- **JourneyLiaisonAgent**: `realms/journey/agents/journey_liaison_agent.py`
  - Interactive SOP generation
  - Conversation-based requirement gathering
- **InsightsLiaisonAgent**: `realms/insights/agents/insights_liaison_agent.py`
  - Interactive deep dive analysis
  - Question answering about data
- **OutcomesLiaisonAgent**: `realms/outcomes/agents/outcomes_liaison_agent.py`
  - (Likely similar pattern)

**Landing Page**:
- Location: `symphainy-frontend/app/(public)/page.tsx`
- Current: Public entry point
- Missing: Coexistence concept introduction

---

## 3. Proposed Architecture

### Landing Page → Coexistence Introduction

**Landing Page** introduces:
1. **Coexistence Concept**: "How humans interact with the platform"
2. **GuideAgent**: "Your platform concierge"
3. **Solution Navigation**: "Explore solutions through conversation"

**User Experience:**
```
Landing Page
├── Welcome Message
├── Coexistence Concept Introduction
│   └── "Every solution has a coexistence component - 
│        your interface to the platform"
├── GuideAgent Introduction
│   └── "Meet your platform concierge - 
│        GuideAgent helps you navigate and interact"
└── Solution Navigation
    └── "Start a conversation to explore solutions"
```

### Solution → Coexistence Component

**Every Solution** includes:
1. **GuideAgent** (Platform-level concierge)
   - Routes to solution-specific liaison agents
   - Provides platform navigation
   - Understands solution context

2. **Solution-Specific Liaison Agents** (Solution-level conversational interface)
   - Provide solution-specific guidance
   - Handle solution-specific conversations
   - Route to solution journeys/intents

**Pattern:**
```
Solution: File Management Solution
├── Business Logic
│   ├── Journey: File Upload & Processing
│   ├── Journey: File Search & Discovery
│   └── Journey: File Archive & Retention
└── Coexistence Component
    ├── GuideAgent (Platform-level)
    │   └── Routes to ContentLiaisonAgent
    └── ContentLiaisonAgent (Solution-level)
        └── Provides file management conversational interface
```

### GuideAgent → Liaison Agent Routing

**GuideAgent** routes based on:
1. **Solution Context**: Which solution is the user in?
2. **User Intent**: What is the user trying to accomplish?
3. **Conversation State**: What has the user already done?

**Routing Logic:**
```
User Message → GuideAgent
├── Analyze Intent
├── Determine Solution Context
└── Route to Appropriate Liaison Agent
    ├── ContentLiaisonAgent (for Content/File Management solutions)
    ├── InsightsLiaisonAgent (for Insights solutions)
    ├── JourneyLiaisonAgent (for Journey/Operations solutions)
    └── OutcomesLiaisonAgent (for Outcomes solutions)
```

---

## 4. Architectural Boundaries

### ✅ **No Boundary Violations**

**Platform Level** (Civic Systems):
- **GuideAgent**: Platform-level concierge
- **Agent Framework**: Base classes and infrastructure
- **MCP Servers**: Expose orchestrators as MCP tools

**Solution Level** (Solutions):
- **Liaison Agents**: Solution-specific conversational interfaces
- **Journeys**: Solution workflows
- **UI Components**: Solution user interfaces

**Realm Level** (Realms):
- **Intent Services**: Platform capabilities
- **Enabling Services**: Domain logic
- **Orchestrators**: Journey-level composition (in Journey Realm)

**Clear Separation:**
- GuideAgent is **platform-level** (civic_systems)
- Liaison agents are **solution-level** (realms/solutions)
- Solutions compose journeys, which use orchestrators, which use agents
- This is just clarifying that solutions have a "coexistence interface"

---

## 5. Solution Contract Enhancement

### Updated Solution Contract Template

Add **Coexistence Component** section:

```markdown
## 10. Coexistence Component

### Human Interaction Interface
This solution provides a coexistence component for human-platform interaction.

**GuideAgent Integration:**
- **Platform Concierge**: GuideAgent routes to solution-specific liaison agents
- **Navigation**: GuideAgent helps users navigate solution capabilities
- **Context Awareness**: GuideAgent understands solution context

**Solution-Specific Liaison Agents:**
- **Liaison Agent**: [Agent Name] (e.g., ContentLiaisonAgent)
- **Capabilities**: [What the liaison agent can do]
- **Conversation Topics**: [What users can discuss with the liaison agent]

**Example:**
- **Solution**: File Management Solution
- **Liaison Agent**: ContentLiaisonAgent
- **Capabilities**: 
  - Help users upload files
  - Explain file processing steps
  - Answer questions about file status
  - Guide users through file management workflows
```

---

## 6. Concrete Example: File Management Solution

### Solution Structure

```
File Management Solution
├── Business Logic
│   ├── Journey: File Upload & Processing
│   ├── Journey: File Search & Discovery
│   └── Journey: File Archive & Retention
├── UI Components
│   ├── File Upload UI
│   ├── File Search UI
│   └── File Archive UI
└── Coexistence Component
    ├── GuideAgent (Platform-level)
    │   └── Routes to ContentLiaisonAgent
    └── ContentLiaisonAgent (Solution-level)
        └── Conversational Interface:
            - "How do I upload a file?"
            - "What happens after I upload?"
            - "How do I search for files?"
            - "How do I archive files?"
```

### User Experience Flow

```
1. User lands on Landing Page
   └── Sees coexistence concept introduction
   └── Sees GuideAgent introduction

2. User navigates to File Management Solution
   └── GuideAgent greets user
   └── GuideAgent routes to ContentLiaisonAgent

3. User interacts with ContentLiaisonAgent
   └── "How do I upload a file?"
   └── ContentLiaisonAgent explains process
   └── ContentLiaisonAgent can trigger Journey: File Upload & Processing

4. User uploads file via UI
   └── Journey: File Upload & Processing executes
   └── ContentLiaisonAgent can answer questions about status

5. User asks ContentLiaisonAgent questions
   └── "What's the status of my file?"
   └── ContentLiaisonAgent queries artifact state
   └── ContentLiaisonAgent provides conversational response
```

---

## 7. Landing Page Implementation

### Landing Page Structure

```tsx
// app/(public)/page.tsx
export default function LandingPage() {
  return (
    <div>
      {/* Welcome Section */}
      <WelcomeSection />
      
      {/* Coexistence Concept Introduction */}
      <CoexistenceIntroduction>
        <h2>How Humans Interact with the Platform</h2>
        <p>
          Every solution has a coexistence component - 
          your interface to the platform. This is how you 
          interact with SymphAIny through conversation.
        </p>
      </CoexistenceIntroduction>
      
      {/* GuideAgent Introduction */}
      <GuideAgentIntroduction>
        <h2>Meet Your Platform Concierge</h2>
        <p>
          GuideAgent is your platform concierge. It helps you 
          navigate solutions, understand capabilities, and 
          interact with the platform through conversation.
        </p>
        <ChatInterface agent="guide_agent" />
      </GuideAgentIntroduction>
      
      {/* Solution Navigation */}
      <SolutionNavigation>
        <h2>Explore Solutions</h2>
        <SolutionCards>
          <SolutionCard 
            name="File Management"
            description="Upload, process, and manage files"
            coexistenceAgent="content_liaison_agent"
          />
          <SolutionCard 
            name="Data Insights"
            description="Analyze data and generate insights"
            coexistenceAgent="insights_liaison_agent"
          />
          {/* ... more solutions */}
        </SolutionCards>
      </SolutionNavigation>
    </div>
  );
}
```

---

## 8. Solution Registry Enhancement

### Solution Registry Schema

Add **coexistence_component** field:

```sql
CREATE TABLE solutions (
  solution_id VARCHAR(255) PRIMARY KEY,
  solution_name VARCHAR(255) NOT NULL,
  solution_version VARCHAR(50) NOT NULL,
  status VARCHAR(50) NOT NULL,
  coexistence_component JSONB,  -- NEW FIELD
  -- ... other fields
);

-- coexistence_component structure:
{
  "guide_agent_enabled": true,
  "liaison_agents": [
    {
      "agent_id": "content_liaison_agent",
      "agent_type": "conversational",
      "capabilities": ["file_upload_guidance", "file_status_queries"],
      "solution_context": "file_management"
    }
  ]
}
```

---

## 9. Implementation Strategy

### Phase 1: Landing Page Enhancement
- Add coexistence concept introduction
- Add GuideAgent introduction
- Add solution navigation with coexistence components

### Phase 2: Solution Contract Enhancement
- Update solution contract template with coexistence component section
- Document GuideAgent integration
- Document liaison agent capabilities

### Phase 3: Solution Registry Enhancement
- Add coexistence_component field to solution registry
- Register coexistence components for existing solutions
- Create solution registry API endpoints

### Phase 4: GuideAgent Enhancement
- Enhance GuideAgent routing logic for solutions
- Add solution context awareness
- Add liaison agent routing

### Phase 5: Liaison Agent Enhancement
- Ensure all solutions have liaison agents
- Document liaison agent capabilities
- Create liaison agent registry

---

## 10. Questions for CIO/CTO

1. **Coexistence Component:**
   - Should every solution have a coexistence component?
   - Is GuideAgent + Liaison Agents the right pattern?
   - Should coexistence components be optional or required?

2. **Landing Page:**
   - Should the landing page introduce coexistence concept?
   - Should the landing page introduce GuideAgent?
   - Should the landing page be a solution itself?

3. **Liaison Agents:**
   - Should liaison agents be solution-specific or realm-specific?
   - Should liaison agents be required for all solutions?
   - How do liaison agents relate to journeys?

4. **Solution Registry:**
   - Should coexistence components be registered in solution registry?
   - Should coexistence components be versioned?
   - How do coexistence components evolve?

5. **User Experience:**
   - Should users always interact through GuideAgent?
   - Can users interact directly with liaison agents?
   - How do UI components relate to coexistence components?

---

## 11. Recommendation

### ✅ **Proceed with Coexistence Component Architecture**

**Why:**
1. **Consistent Pattern**: Every solution has a coexistence component
2. **Clear Boundaries**: Platform-level (GuideAgent) vs Solution-level (liaison agents)
3. **User-Friendly**: Landing page introduces the concept
4. **Scalable**: New solutions can add their own liaison agents
5. **No Boundary Violations**: Clear separation of concerns

**How:**
1. **Phase 1:** Enhance landing page with coexistence concept introduction
2. **Phase 2:** Update solution contract template with coexistence component section
3. **Phase 3:** Enhance solution registry with coexistence_component field
4. **Phase 4:** Enhance GuideAgent routing for solutions
5. **Phase 5:** Ensure all solutions have liaison agents

**Validation:**
- Validate with CIO/CTO at each phase
- Test coexistence component integration at each phase
- Ensure user experience is intuitive

---

## 12. Conclusion

**Coexistence Component Architecture** provides:
- **Consistent Pattern**: Every solution has a coexistence component
- **Clear Boundaries**: Platform-level vs Solution-level
- **User-Friendly**: Landing page introduces the concept
- **Scalable**: New solutions can add their own liaison agents

**This is the missing piece** that clarifies how humans interact with solutions.

---

**Last Updated:** January 27, 2026  
**Owner:** Development Team
