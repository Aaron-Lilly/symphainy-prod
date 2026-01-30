# Insights Capability

**What it does:** Semantic interpretation, data quality, analysis, and relationship mapping.

**Core functions:**
- Business analysis and interpretation
- Data quality assessment
- Data analysis workflows
- Lineage visualization
- Relationship mapping between entities

**MVP exposure:** `experience/insights`

**Current implementation:** `realms/insights/intent_services/`

**Intent types:**
- `analyze_business_context` — Business-level interpretation
- `assess_data_quality` — Quality metrics and issues
- `analyze_data` — Statistical and semantic analysis
- `map_relationships` — Entity relationship discovery
- `visualize_lineage` — Data lineage tracing

**Layer:** Execution Plane (below SDK boundary) — may access Public Works and State Surface directly.
