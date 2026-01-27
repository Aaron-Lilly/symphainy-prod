# Cursor Web Agents Guide for SymphAIny Coexistence Fabric

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

## Solution Components

Every solution needs:
1. **Security** (Login/Authentication)
2. **Control Tower** (Admin Dashboard/Observability)
3. **Coexistence** (Landing Page/Human Interface)
4. **Policies** (Smart City Primitives - enforced by default)
5. **Experiences** (REST API and Websockets)
6. **Business Logic** (Journeys → Intents)

## Current Work

We're building the MVP with 4 foundational solutions:

1. **Security Solution** - Authentication and authorization
2. **Coexistence Solution** - Human-platform interaction interface
3. **Control Tower Solution** - Platform observability and administration
4. **Platform MVP Solution** - Core platform capabilities (Content, Insights, Journey, Outcomes)

## What to Build

### Phase 1: Create Contracts First
1. Create solution contracts for all 4 MVP solutions
2. Create journey contracts for each solution
3. Create intent contracts for each journey
4. Validate contracts for completeness

### Phase 2: Build Solution Components
1. Extract intent services from old orchestrators (reference only)
2. Create intent services in realms
3. Create journey orchestrators in Journey Realm
4. Create solution implementations
5. Generate tests
6. Validate against contracts

## Contract Locations

- Intent Contracts: `docs/intent_contracts/`
- Journey Contracts: `docs/journey_contracts/`
- Solution Contracts: `docs/solution_contracts/`

## Testing

- Contract-based testing required
- All intents must align to contracts
- All journeys must align to contracts
- All solutions must align to contracts
- 3D testability (same rigor as current contracts)

## Project Structure

```
symphainy_coexistence_fabric/
├── foundations/          # Public Works, Curator
├── runtime/              # Runtime API, Execution Lifecycle Manager, State Surface
├── utilities/            # logging, clock, errors, ids
├── civic_systems/       # Smart City, Agentic, Experience
├── solutions/           # Top-level solutions
├── realms/              # Content, Insights, Journey, Outcomes
├── journey_realm/       # Orchestrators live here
├── docs/
│   ├── intent_contracts/
│   ├── journey_contracts/
│   └── solution_contracts/
└── tests/
```

## Key Constraints

- **No Backward Compatibility:** Clean break from old architecture
- **Contract-Based Testing:** All code must align to contracts
- **Artifact-Centric Only:** No file-centric patterns
- **Solution Contracts First:** Create contracts before building

## Agent Instructions

When building solution components:

1. **Read Contracts First:**
   - Read solution contract
   - Read journey contracts
   - Read intent contracts

2. **Generate Code:**
   - Create intent services in realms
   - Create journey orchestrators in Journey Realm
   - Create solution implementations
   - Generate tests

3. **Validate:**
   - Validate against contracts
   - Run contract tests
   - Check architecture compliance

4. **Create PR:**
   - Create PR with changes
   - Include contract validation results
   - Document any deviations

## Reference Documentation

- MVP Solution Architecture: `../docs/01242026_final/MVP_SOLUTION_ARCHITECTURE_AND_MIGRATION_STRATEGY.md`
- Coexistence Fabric Vision: `../docs/01242026_final/COEXISTENCE_FABRIC_IMPLEMENTATION_VISION.md`
- Solution Contract Recommendation: `../docs/01242026_final/SOLUTION_CONTRACT_RECOMMENDATION.md`
- Architectural Epiphany: `../docs/01242026_final/ARCHITECTURAL_EPIPHANY_ANALYSIS.md`
