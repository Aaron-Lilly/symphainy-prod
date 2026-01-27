# Journey: Cross-Pillar Integration - Intent Contracts

**Journey ID:** `journey_solution_cross_pillar_integration`

## Consolidation Notice

⚠️ **The original intents for this journey have been consolidated into `synthesize_outcome`.**

### Original Intents (Deprecated)
1. `load_cross_pillar_data` - ❌ Removed (now part of `synthesize_outcome`)
2. `create_summary_visualization` - ❌ Removed (now part of `synthesize_outcome`)
3. `display_realm_contributions` - ❌ Removed (now part of `synthesize_outcome`)

### Current Implementation
The cross-pillar integration functionality is now handled by the `synthesize_outcome` intent in the Solution Synthesis journey:

- **Intent:** `synthesize_outcome`
- **Location:** `journey_solution_synthesis/intent_synthesize_outcome.md`

### What `synthesize_outcome` Does
1. Reads pillar summaries from session state (load_cross_pillar_data)
2. Generates realm-specific visuals (display_realm_contributions)
3. Creates summary visualization (create_summary_visualization)
4. Returns unified synthesis artifact

### Why Consolidated
- Simpler frontend integration (single intent)
- Reduced API calls
- Unified artifact structure
- Better performance

---

**See:** `journey_solution_synthesis/intent_synthesize_outcome.md` for the current implementation.
