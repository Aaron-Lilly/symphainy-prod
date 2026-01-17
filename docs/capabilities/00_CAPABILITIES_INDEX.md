# Platform Capabilities Index

**Last Updated:** January 2026  
**Status:** Current Platform Truth

---

## Overview

This directory documents all capabilities available in the Symphainy Platform. Capabilities are organized by **Realm** (domain service area) and represent what the platform can do today.

**Key Principle:** These are **current capabilities**, not planned features. Everything listed here is implemented and operational.

---

## Capabilities by Realm

### Content Realm
**Purpose:** File management, data ingestion, parsing, and normalization

**Capabilities:**
- [File Management](file_management.md) - Register, retrieve, list, and manage files
- [Data Ingestion](data_ingestion.md) - Ingest files via upload, EDI, or API
- [File Parsing](file_parsing.md) - Parse diverse file types (PDF, Excel, binary, images, BPMN, DOCX)
- [Bulk Operations](bulk_operations.md) - Process thousands of files efficiently
- [File Lifecycle](file_lifecycle.md) - Archive, restore, purge, validate, search, and manage file lifecycle

**Status:** ✅ Complete (Phases 1-4)

---

### Insights Realm
**Purpose:** Data quality assessment, semantic interpretation, and analysis

**Capabilities:**
- [Data Quality Assessment](data_quality.md) - Assess data quality, identify issues
- [Semantic Interpretation](semantic_interpretation.md) - Understand data meaning and relationships
- [Interactive Analysis](interactive_analysis.md) - Analyze structured and unstructured data
- [Guided Discovery](guided_discovery.md) - Systematically explore data
- [Lineage Tracking](lineage_tracking.md) - Track data origins and transformations

**Status:** ✅ Complete

---

### Journey Realm
**Purpose:** Workflow creation, SOP generation, and process optimization

**Capabilities:**
- [Workflow Creation](workflow_creation.md) - Create workflows from BPMN models
- [SOP Generation](sop_generation.md) - Generate SOPs from interactive conversations
- [Visual Generation](visual_generation.md) - Automatically generate workflow diagrams
- [Coexistence Analysis](coexistence_analysis.md) - Understand process interactions
- [Coexistence Blueprint](coexistence_blueprint.md) - Create implementation blueprints with workflow charts and responsibility matrix

**Status:** ✅ Complete

---

### Outcomes Realm
**Purpose:** Solution synthesis, roadmap generation, and business outcomes

**Capabilities:**
- [Solution Synthesis](solution_synthesis.md) - Synthesize solutions from multiple insights
- [Roadmap Generation](roadmap_generation.md) - Generate implementation roadmaps
- [POC Creation](poc_creation.md) - Create proof of concept documents

**Status:** ✅ Complete

---

## Admin Dashboard
**Civic System:** Experience Plane  
**Purpose:** Platform management, development tools, and solution composition

**Capabilities:**
- [Admin Dashboard](admin_dashboard.md) - Control Room (observability), Developer View (SDK docs & tools), Business User View (solution composition)

**Status:** ✅ Complete

---

## Agent Capabilities

### Guide Agent
**Purpose:** Global concierge for platform navigation

**Capabilities:**
- User intent analysis
- Platform navigation guidance
- Pillar recommendation
- Routing to liaison agents

**Status:** ✅ Complete

### Liaison Agents
**Purpose:** Domain experts for each realm

**Capabilities:**
- Content Liaison Agent - File management guidance
- Insights Liaison Agent - Data analysis guidance
- Journey Liaison Agent - Workflow and SOP guidance
- Outcomes Liaison Agent - Solution guidance

**Status:** ✅ Complete

---

## Infrastructure Capabilities

### Multi-Tenant Safety
- Tenant data isolation
- Operation scoping to tenant context
- Compliance enforcement

### File Storage
- GCS integration
- File metadata management
- File lifecycle tracking

### State Management
- Redis (hot state)
- ArangoDB (durable state)
- State Surface (governed access)

### Search & Discovery
- Meilisearch integration
- File search and query
- Metadata search

---

## How to Use This Documentation

### For Developers
1. **Find a capability** → Read the detailed capability document
2. **See examples** → Each capability document includes code examples
3. **Check API contracts** → See [API Contracts](../execution/api_contracts_frontend_integration.md) for request/response formats

### For Product Managers
1. **Understand what's available** → Review capability summaries
2. **See use cases** → Each capability document includes business use cases
3. **Check status** → See which capabilities are complete vs in progress

### For Executives
1. **High-level overview** → See [Platform Overview](../PLATFORM_OVERVIEW.md)
2. **Business value** → Each capability document explains business value
3. **Current status** → This index shows what's operational today

---

## Quick Reference

**Need to upload a file?**
→ See [Data Ingestion](data_ingestion.md)

**Need to analyze data quality?**
→ See [Data Quality Assessment](data_quality.md)

**Need to create a workflow?**
→ See [Workflow Creation](workflow_creation.md)

**Need to understand what intents are available?**
→ See [API Contracts](../execution/api_contracts_frontend_integration.md)

---

## Capability Status Summary

| Realm/System | Capabilities | Status |
|-------------|-------------|--------|
| Content | 5 capability areas | ✅ Complete |
| Insights | 5 capability areas | ✅ Complete |
| Journey | 5 capability areas | ✅ Complete |
| Outcomes | 3 capability areas | ✅ Complete |
| Admin Dashboard | 1 capability area (3 views) | ✅ Complete |
| Agents | 2 agent types | ✅ Complete |
| Infrastructure | 4 capability areas | ✅ Complete |

**Total Operational Capabilities:** 25 capability areas (1 implementation in progress)

---

## Related Documentation

- [Platform Overview](../PLATFORM_OVERVIEW.md) - Executive overview
- [API Contracts](../execution/api_contracts_frontend_integration.md) - Technical API reference
- [Architecture Guide](../architecture/north_star.md) - How capabilities are built
- [Platform Rules](../PLATFORM_RULES.md) - Development standards

---

**Questions?** See individual capability documents for detailed information.
