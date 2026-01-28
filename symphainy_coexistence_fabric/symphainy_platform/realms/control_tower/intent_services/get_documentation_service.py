"""
Get Documentation Intent Service

Implements the get_documentation intent for the Control Tower Realm.

Purpose: Retrieve platform documentation for a specific topic.

WHAT (Intent Service Role): I provide platform documentation
HOW (Intent Service Implementation): I return documentation
    organized by topic and category
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class GetDocumentationService(BaseIntentService):
    """
    Intent service for retrieving platform documentation.
    
    Provides documentation on:
    - Architecture overview
    - Getting started guides
    - API references
    - Best practices
    """
    
    DOCUMENTATION = {
        "architecture_overview": {
            "title": "Platform Architecture Overview",
            "category": "architecture",
            "content": """
# SymphAIny Platform Architecture

## Core Principles
1. **Runtime owns execution** - Nothing executes without Runtime's knowledge
2. **Intent-based architecture** - All operations expressed as intents
3. **Public Works pattern** - All infrastructure via abstractions
4. **Multi-tenant safety** - Built-in tenant isolation

## Layer Model
- **Solutions** - User-facing capabilities (compose journeys, expose APIs)
- **Journeys** - Orchestrate sequences of intents
- **Realms** - Domain-specific intent services
- **Foundations** - Infrastructure abstractions (Public Works)
- **Runtime** - Execution, state, artifacts

## Key Components
- **Intent Services**: Atomic capabilities in Realms
- **Journey Orchestrators**: Sequence intents in Solutions
- **MCP Servers**: Expose Solution tools to agents
- **State Surface**: Manages execution and artifact state
- **Public Works**: Infrastructure abstraction layer
""",
            "related_topics": ["realms", "solutions", "public_works"]
        },
        "realms": {
            "title": "Realms - Domain Services",
            "category": "architecture",
            "content": """
# Realms

Realms contain domain-specific intent services organized by business capability.

## Available Realms
- **Content**: File ingestion, parsing, content management
- **Insights**: Analysis, extraction, intelligence generation
- **Operations**: Workflow/SOP management, coexistence analysis
- **Outcomes**: Outcomes synthesis, roadmaps, POCs, blueprints
- **Security**: Authentication, authorization, session management
- **Control Tower**: Platform administration, monitoring
- **Coexistence**: Platform entry, navigation, agent interactions

## Correct Pattern
Realms should ONLY contain:
- `__init__.py`
- `intent_services/`

## Anti-Patterns (Forbidden)
- `orchestrators/` - Runtime handles orchestration
- `mcp_server/` - MCP servers belong in Solutions
- `agents/` - Agents belong in civic_systems/agentic/agents/
""",
            "related_topics": ["intent_services", "solutions", "architecture_overview"]
        },
        "solutions": {
            "title": "Solutions - Platform Capabilities",
            "category": "architecture",
            "content": """
# Solutions

Solutions are top-level platform constructs that compose Journeys and expose SOA APIs.

## Solution Responsibilities
1. Compose Journey orchestrators
2. Expose SOA APIs via get_soa_apis()
3. Register MCP Server for agent access
4. Handle compose_journey intents

## Available Solutions
- **ContentSolution**: File management capabilities
- **InsightsSolution**: Data analysis capabilities
- **OperationsSolution**: Workflow and SOP capabilities
- **OutcomesSolution**: Strategic deliverable capabilities
- **CoexistenceSolution**: Platform entry and navigation

## Creating a Solution
1. Create directory in `symphainy_platform/solutions/`
2. Implement Solution class extending SolutionBase
3. Create Journey orchestrators
4. Create MCP Server
5. Register in solution_initializer.py
""",
            "related_topics": ["journeys", "mcp_servers", "realms"]
        },
        "public_works": {
            "title": "Public Works - Infrastructure Abstractions",
            "category": "infrastructure",
            "content": """
# Public Works Pattern

All infrastructure access must go through Public Works abstractions.

## Available Abstractions
- **file_storage_abstraction**: File upload/download (GCS)
- **state_abstraction**: State storage (Redis)
- **registry_abstraction**: Entity registry (Postgres)
- **auth_abstraction**: Authentication/authorization
- **telemetry_abstraction**: Metrics and tracing
- **artifact_storage_abstraction**: Artifact persistence

## Usage
```python
# CORRECT - Use abstraction
file_storage = public_works.file_storage_abstraction
await file_storage.upload_file(content, path)

# WRONG - Direct adapter access
await gcs_adapter.upload(...)  # Anti-pattern!
```

## Benefits
- Consistent interface across infrastructure
- Built-in retry, error handling, logging
- Easy testing with mock abstractions
- Loose coupling from infrastructure
""",
            "related_topics": ["architecture_overview", "intent_services"]
        },
        "intent_services": {
            "title": "Intent Services - Atomic Capabilities",
            "category": "development",
            "content": """
# Intent Services

Intent services are atomic capabilities that handle single intent types.

## Characteristics
- Handle ONE intent type
- Use Public Works for infrastructure
- Register artifacts with State Surface
- Record telemetry via Nurse SDK

## Creating an Intent Service
1. Create file in `realms/{realm}/intent_services/`
2. Extend BaseIntentService
3. Implement execute() method
4. Export in __init__.py
5. Register in service_factory.py

## Example Structure
```python
class MyIntentService(BaseIntentService):
    def __init__(self, public_works, state_surface):
        super().__init__(
            service_id="my_intent_service",
            intent_type="my_intent",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(self, context, params=None):
        # Handle the intent
        pass
```
""",
            "related_topics": ["realms", "public_works", "solutions"]
        },
        "getting_started": {
            "title": "Getting Started",
            "category": "guides",
            "content": """
# Getting Started with SymphAIny Platform

## Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Access to GCP (for storage)

## Quick Start
1. Clone repository
2. Run `docker-compose up`
3. Access API at http://localhost:8000

## Key Entry Points
- **Runtime API**: `/api/v1/intents/` - Execute intents
- **Experience API**: `/api/v1/experience/` - Frontend integration
- **Admin API**: `/api/v1/admin/` - Platform management

## First Steps
1. Authenticate via Security Realm
2. Create a session
3. Execute intents via Runtime API
4. View artifacts in State Surface

## Documentation
- Architecture: docs/architecture/north_star.md
- API Contracts: docs/execution/api_contracts_*.md
- Capabilities: docs/capabilities/00_CAPABILITIES_INDEX.md
""",
            "related_topics": ["architecture_overview", "realms", "solutions"]
        }
    }
    
    def __init__(self, public_works, state_surface):
        """Initialize GetDocumentationService."""
        super().__init__(
            service_id="get_documentation_service",
            intent_type="get_documentation",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the get_documentation intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            topic = intent_params.get("topic")  # Optional
            category = intent_params.get("category")  # Optional filter
            list_only = intent_params.get("list_only", False)
            
            if topic:
                if topic not in self.DOCUMENTATION:
                    raise ValueError(f"Unknown topic: {topic}")
                docs = {topic: self.DOCUMENTATION[topic]}
            elif category:
                docs = {
                    k: v for k, v in self.DOCUMENTATION.items()
                    if v.get("category") == category
                }
            else:
                docs = self.DOCUMENTATION
            
            # Return just titles if list_only
            if list_only:
                docs = {
                    k: {"title": v["title"], "category": v["category"]}
                    for k, v in docs.items()
                }
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success"},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "documentation": docs,
                "topic_count": len(docs),
                "categories": list(set(d["category"] for d in self.DOCUMENTATION.values())),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except ValueError as e:
            return {"success": False, "error": str(e), "error_code": "INVALID_TOPIC"}
        except Exception as e:
            self.logger.error(f"Failed to get documentation: {e}")
            return {"success": False, "error": str(e), "error_code": "GET_DOCS_ERROR"}
