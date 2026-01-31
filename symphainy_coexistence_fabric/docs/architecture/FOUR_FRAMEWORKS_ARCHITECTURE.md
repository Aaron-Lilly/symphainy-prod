# Four Frameworks Architecture

**Status:** Canonical (January 2026)
**Authors:** Team B (Landing) with CTO alignment
**Purpose:** Define the strategic product architecture embedded in SymphAIny's platform design

> **SymphAIny is the Intent-Driven Enterprise Operating System that transforms how organizations integrate, reason, and execute — using intent as the semantic kernel to modernize operations without rewrites and turn integration expertise into reusable products.**

---

## Executive Summary

SymphAIny's platform is organized around **Four Pre-configured Solution Frameworks** that represent different levels of platform maturity and client engagement:

| Framework | Delivery Model | Client Value |
|-----------|---------------|--------------|
| **Content** | Fully functional | Real content management |
| **Insights** | Fully functional | Real data understanding |
| **Operations** | Demonstrative (teaser) | Blueprint for transformation |
| **Outcomes** | Demonstrative (teaser) | Proposal for business results |

This is not an accident—it's a **product strategy embedded in the architecture**.

---

## 1. The Two-Tier Model

### Tier 1: "Keys to the Castle" (Fully Functional)

```
┌─────────────────────────────────────────────────────────────┐
│  CONTENT FRAMEWORK                                          │
│                                                             │
│  Real capabilities:                                         │
│  • Parse any file type (PDF, Excel, CSV, JSON, etc.)       │
│  • Ingest and store with full metadata                      │
│  • Create deterministic embeddings                          │
│  • Manage file lifecycle (archive, delete, retrieve)        │
│                                                             │
│  Client gets: ACTUAL content management                     │
│  Self-service: Yes                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  INSIGHTS FRAMEWORK                                         │
│                                                             │
│  Real capabilities:                                         │
│  • Analyze structured and unstructured data                 │
│  • Assess data quality with AI-powered recommendations      │
│  • Visualize data lineage and provenance                    │
│  • Map relationships and patterns                           │
│  • AI-guided interpretation                                 │
│                                                             │
│  Client gets: ACTUAL insights from their data               │
│  Self-service: Yes                                          │
└─────────────────────────────────────────────────────────────┘
```

### Tier 2: "Teasing What's Possible" (Demonstrative)

```
┌─────────────────────────────────────────────────────────────┐
│  OPERATIONS FRAMEWORK                                       │
│                                                             │
│  Teaser capabilities:                                       │
│  • Generate Coexistence Blueprints                          │
│  • Create workflow visualizations                           │
│  • Produce SOP documents                                    │
│  • Analyze human-AI coexistence opportunities               │
│                                                             │
│  Client gets: PLAN for transformed operations               │
│  Not yet delivered: Actual transformed operations           │
│  Engagement opportunity: Yes                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  OUTCOMES FRAMEWORK                                         │
│                                                             │
│  Teaser capabilities:                                       │
│  • Generate POC Proposals                                   │
│  • Create Implementation Roadmaps                           │
│  • Synthesize session outcomes                              │
│  • Produce solution blueprints                              │
│                                                             │
│  Client gets: PROPOSAL for business outcomes                │
│  Not yet delivered: Actual business outcomes                │
│  Engagement opportunity: Yes                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. The Client Journey

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: EXPERIENCE VALUE                                  │
│                                                             │
│  Client uses Content + Insights frameworks                  │
│  • Uploads their data                                       │
│  • Gets real parsing, analysis, quality assessment          │
│  • Sees the platform actually works                         │
│                                                             │
│  Outcome: Trust established, value demonstrated             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: SEE WHAT'S POSSIBLE                               │
│                                                             │
│  Client explores Operations + Outcomes frameworks           │
│  • Sees AI-generated Coexistence Blueprint                  │
│  • Reviews POC Proposal with roadmap                        │
│  • Understands transformation potential                     │
│                                                             │
│  Outcome: Vision established, appetite created              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: ENGAGE TO BUILD                                   │
│                                                             │
│  Client engages to implement actual Operations + Outcomes   │
│  • Blueprint becomes real transformation                    │
│  • Proposal becomes delivered outcome                       │
│  • Custom intent services built for their needs             │
│                                                             │
│  Outcome: Real business value delivered                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Relationship to Platform Composition Model

The Four Frameworks are **orthogonal** to the Platform Composition Model:

### Platform Composition Model (HOW things orchestrate)

```
Solution
  └── Journey(s)
        └── Intent(s)
```

- **Solution** = A packaged deliverable for a client need
- **Journey** = An orchestrated sequence within a solution
- **Intent** = A single operation within a journey

### Four Frameworks (WHAT gets produced)

```
Content → Insights → Operations → Outcomes
```

- **Content** = Raw material (files, data)
- **Insights** = Understanding (analysis, patterns)
- **Operations** = Process artifacts (workflows, SOPs)
- **Outcomes** = Deliverables (blueprints, POCs, roadmaps)

### How They Interact

Every **Intent** produces artifacts in one of the Four Frameworks:
- Content intents → Content artifacts
- Insight intents → Insight artifacts
- Operations intents → Operations artifacts (blueprints, plans)
- Outcomes intents → Outcomes artifacts (proposals, roadmaps)

**Journeys** orchestrate intents across frameworks.
**Solutions** compose journeys to deliver client value.

---

## 4. Service Architecture Mapping

### The Five Platform Services

| Service | Role in Four Frameworks |
|---------|------------------------|
| **Platform** | Powers Content + Insights (fully functional capabilities) |
| **Agentic** | Powers compelling teasers (AI-generated blueprints, proposals) |
| **Runtime** | Records truth across all frameworks (the spine) |
| **Experience** | Exposes the tiered journey to clients |
| **Smart City** | Governs access (who gets keys to which castle) |

### Service Types

| Type | Frameworks Served | Provider |
|------|-------------------|----------|
| **Enabling Services** | Content + Insights | Platform (included) |
| **Teaser Services** | Operations + Outcomes | Platform (demonstrative) |
| **Intent Services** | Custom implementations | Client engagement (future) |

---

## 5. Why This Architecture

### Strategic Rationale

1. **Demonstrate value immediately** (Content + Insights work out of the box)
2. **Show transformation potential** (Operations + Outcomes tease what's possible)
3. **Create engagement opportunities** (Move from teaser to real implementation)
4. **Enable client self-service** (Tier 1 is fully functional)
5. **Protect implementation complexity** (Tier 2 requires engagement)

### Technical Rationale

1. **Content + Insights are composable** - They're the atomic building blocks
2. **Operations + Outcomes are contextual** - They require client-specific customization
3. **The AI agents shine in Tier 2** - Blueprints and proposals showcase platform intelligence
4. **Runtime captures everything** - Truth recorded regardless of framework

---

## 6. Implementation Status (January 2026)

### Content Framework ✅ Fully Implemented
- `ingest_file` - Upload and store files
- `parse_content` - Parse any file type
- `create_deterministic_embeddings` - Structural embeddings
- `get_parsed_file` - Retrieve parsed content
- `list_artifacts` - Browse artifacts
- `archive_file`, `delete_file` - Lifecycle management

### Insights Framework ✅ Fully Implemented
- `analyze_structured_data` - AI-powered structured analysis
- `analyze_unstructured_data` - AI-powered unstructured analysis
- `assess_data_quality` - Quality with AI recommendations
- `interpret_data_self_discovery` - AI-guided interpretation
- `interpret_data_guided` - Guided discovery with AI suggestions
- `visualize_lineage` - Lineage with AI insights
- `map_relationships` - Relationship mapping

### Operations Framework ✅ Teaser Implemented
- `create_workflow` - Define workflow structure
- `generate_sop` - AI-generated SOP documents
- `generate_sop_from_chat` - Interactive SOP creation
- `analyze_coexistence` - AI-powered coexistence analysis
- **Produces:** Coexistence Blueprints (plans, not implementations)

### Outcomes Framework ✅ Teaser Implemented
- `create_blueprint` - AI-powered blueprint generation
- `create_poc` - AI-powered POC proposals
- `generate_roadmap` - AI-powered implementation roadmaps
- `synthesize_outcome` - Session synthesis
- **Produces:** POC Proposals (proposals, not delivered outcomes)

---

## 7. Future Evolution

### Near-term (Platform Roadmap)
- Enhanced AI reasoning in all frameworks
- More file types in Content framework
- Deeper analysis in Insights framework
- Richer teasers in Operations + Outcomes

### Mid-term (Client Engagements)
- Custom Intent Services for Operations implementations
- Custom Intent Services for Outcomes delivery
- Client-specific workflow automation
- Actual business outcome delivery

### Long-term (Platform Vision)
- Client self-service for Operations + Outcomes
- Tenant-customizable frameworks
- Marketplace for Intent Services
- Full transformation delivery at scale

---

## 8. Key Principles

1. **Tier 1 is the hook** - Real value creates trust
2. **Tier 2 is the vision** - Teasers create appetite
3. **Engagement is the business** - Custom builds deliver transformation
4. **AI powers the teasers** - Blueprints and proposals must be compelling
5. **Runtime records everything** - Truth is the foundation

---

## 9. Three-Layer Intent Model Mapping

The Four Frameworks map to the **Three-Layer Intent Model** (see [THREE_LAYER_INTENT_MODEL.md](THREE_LAYER_INTENT_MODEL.md)):

### Framework to Intent Layer Mapping

| Framework | Primary Intent Layer | IP Ownership | Semantic Role |
|-----------|---------------------|--------------|---------------|
| **Content** | Connective | Platform (Product IP) | System ingestion → Semantic normalization |
| **Insights** | Connective | Platform (Product IP) | Raw data → Semantic understanding |
| **Operations** | Connective + Domain | Platform frameworks + Client implementation | Process choreography + Business workflows |
| **Outcomes** | Domain | Client (Client IP) | Business deliverables (client value) |

### Why This Mapping Matters

```
┌─────────────────────────────────────────────────────────────────┐
│  DOMAIN INTENTS (Client-Owned)                                  │
│  └── Outcomes Framework: Business deliverables                  │
│      └── POC implementations, operational transformations       │
├─────────────────────────────────────────────────────────────────┤
│  CONNECTIVE INTENTS (Platform-Owned, Extensible)                │
│  ├── Operations Framework: Process choreography                 │
│  │   └── Workflow patterns, SOP frameworks, migration           │
│  ├── Insights Framework: Data understanding                     │
│  │   └── Analysis patterns, quality frameworks, lineage         │
│  └── Content Framework: System ingestion                        │
│      └── Parsing patterns, embedding frameworks, normalization  │
├─────────────────────────────────────────────────────────────────┤
│  FOUNDATIONAL INTENTS (Platform-Owned, Core IP)                 │
│  └── Runtime, Governance, Security, Observability               │
└─────────────────────────────────────────────────────────────────┘
```

### Delivery Model Explained by Intent Layer

| Framework | Delivery | Why |
|-----------|----------|-----|
| **Content** | Fully functional | Connective IP — platform owns the integration patterns |
| **Insights** | Fully functional | Connective IP — platform owns the analysis patterns |
| **Operations** | Teaser | Connective frameworks owned; Domain implementation is client-specific |
| **Outcomes** | Teaser | Domain IP — clients own their business outcomes |

**This is the infrastructure moat:** Content and Insights are reusable Connective Intent Packages that apply across industries (VLP, AAR, PSO, etc.).

---

## References

- [THREE_LAYER_INTENT_MODEL.md](THREE_LAYER_INTENT_MODEL.md) - The canonical intent classification
- [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md) - Platform vision alignment
- [FOUR_SERVICE_MAPPING.md](FOUR_SERVICE_MAPPING.md) - Service architecture
- [MEET_IN_THE_MIDDLE_PLAN.md](../MEET_IN_THE_MIDDLE_PLAN.md) - Team integration plan
- [north_star.md](../north_star.md) - Architecture north star
