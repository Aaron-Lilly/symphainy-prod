# Constrained Semantic Reasoning Architecture

**Status:** Architectural Proposal  
**Created:** January 2026  
**Goal:** Enable user-provided fact patterns/data models to constrain semantic reasoning

---

## Executive Summary

Instead of building specialized parsers for each use case (PSO, AAR, etc.), we enable **user-provided fact patterns/data models** that constrain how the platform reasons about data and formats output. This is much more composable and extensible.

---

## Core Insight

**Old Approach (Bolt-on):**
- Hardcode specialized parser for PSO
- Hardcode specialized parser for AAR
- Hardcode specialized parser for each use case
- ❌ Not composable, requires code changes for each new use case

**New Approach (Extensible):**
- Universal semantic interpretation engine
- User-provided fact patterns/data models constrain reasoning
- User-provided output structure templates format results
- ✅ Composable, extensible, no code changes needed

---

## Architectural Pattern

### Layer 1: Universal Semantic Interpretation

**Content Realm:**
- Parses files (structure extraction) - universal
- Generates embeddings - universal
- No specialization needed

**Insights Realm:**
- Semantic interpretation engine - universal
- Uses embeddings to reason about data meaning
- **Accepts constraints** (fact patterns, data models, output templates)

### Layer 2: User-Provided Constraints

**Fact Pattern / Data Model:**
- User-provided schema/ontology
- Defines entities, relationships, attributes
- Constrains what the system looks for

**Output Structure Template:**
- User-provided template for output format
- Defines how results should be structured
- Ensures consistent output format

**Reasoning Constraints:**
- User-provided rules/guidelines
- Constrains how system reasons about data
- Ensures domain-specific interpretation

---

## Use Case Examples

### PSO (Permits) Use Case

**User Provides:**
1. **Fact Pattern:**
   ```json
   {
     "entities": ["permit", "applicant", "property", "regulation"],
     "relationships": [
       {"from": "permit", "to": "applicant", "type": "issued_to"},
       {"from": "permit", "to": "property", "type": "for_property"},
       {"from": "permit", "to": "regulation", "type": "governed_by"}
     ],
     "attributes": {
       "permit": ["id", "type", "status", "issue_date", "expiry_date"],
       "applicant": ["name", "contact", "license_number"],
       "property": ["address", "parcel_id", "zoning"]
     }
   }
   ```

2. **Output Structure Template:**
   ```json
   {
     "permit_id": "...",
     "permit_type": "...",
     "status": "...",
     "applicant": {
       "name": "...",
       "contact": "..."
     },
     "property": {
       "address": "...",
       "parcel_id": "..."
     },
     "regulations": [...]
   }
   ```

**System Behavior:**
- Uses universal semantic interpretation
- Constrains reasoning to look for permit entities, relationships, attributes
- Formats output according to template
- No specialized parser needed!

### AAR (After Action Reports) Use Case

**User Provides:**
1. **Fact Pattern:**
   ```json
   {
     "entities": ["event", "action", "outcome", "lesson_learned"],
     "relationships": [
       {"from": "event", "to": "action", "type": "triggered"},
       {"from": "action", "to": "outcome", "type": "resulted_in"},
       {"from": "outcome", "to": "lesson_learned", "type": "yielded"}
     ],
     "attributes": {
       "event": ["description", "timestamp", "location"],
       "action": ["description", "actor", "timestamp"],
       "outcome": ["description", "success", "metrics"],
       "lesson_learned": ["description", "category", "priority"]
     }
   }
   ```

2. **Output Structure Template:**
   ```json
   {
     "event_summary": "...",
     "actions_taken": [
       {
         "description": "...",
         "actor": "...",
         "outcome": "..."
       }
     ],
     "lessons_learned": [
       {
         "description": "...",
         "category": "...",
         "priority": "..."
       }
     ]
   }
   ```

**System Behavior:**
- Same universal semantic interpretation engine
- Different constraints (AAR fact pattern)
- Different output format (AAR template)
- No specialized parser needed!

### Data Mapping (Data Mash) Use Case

**User Provides:**
1. **Mapping Schema:**
   ```json
   {
     "source_entities": ["policy", "claim", "customer"],
     "target_entities": ["policy_new", "claim_new", "customer_new"],
     "mappings": [
       {
         "source": "policy.policy_number",
         "target": "policy_new.external_id",
         "transformation": "prefix_with_legacy_"
       },
       {
         "source": "claim.claim_amount",
         "target": "claim_new.total_amount",
         "transformation": "currency_conversion"
       }
     ],
     "relationships": [
       {
         "source": "policy -> claim",
         "target": "policy_new -> claim_new",
         "preserve": true
       }
     ]
   }
   ```

2. **Virtual Pipeline Configuration:**
   ```json
   {
     "virtual": true,
     "no_ingestion": true,
     "query_only": true,
     "lineage_tracking": true
   }
   ```

**System Behavior:**
- Uses universal semantic interpretation
- Applies mapping schema to create virtual relationships
- No data ingestion (virtual pipeline)
- Relationships stored in ArangoDB graph
- Lineage tracked in Supabase

---

## Implementation Architecture

### New Components

#### 1. Fact Pattern Registry

**Location:** `symphainy_platform/civic_systems/platform_sdk/fact_pattern_registry.py`

**Purpose:** Store and manage user-provided fact patterns

**Interface:**
```python
class FactPatternRegistry:
    async def register_fact_pattern(
        self,
        pattern_id: str,
        fact_pattern: Dict[str, Any],
        tenant_id: str
    ) -> bool
    
    async def get_fact_pattern(
        self,
        pattern_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]
    
    async def list_fact_patterns(
        self,
        tenant_id: str
    ) -> List[Dict[str, Any]]
```

**Storage:** Supabase (fact_patterns table)

#### 2. Output Template Registry

**Location:** `symphainy_platform/civic_systems/platform_sdk/output_template_registry.py`

**Purpose:** Store and manage user-provided output templates

**Interface:**
```python
class OutputTemplateRegistry:
    async def register_template(
        self,
        template_id: str,
        template: Dict[str, Any],
        tenant_id: str
    ) -> bool
    
    async def get_template(
        self,
        template_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]
```

**Storage:** Supabase (output_templates table)

#### 3. Constrained Semantic Interpreter

**Location:** `symphainy_platform/realms/insights/enabling_services/constrained_semantic_interpreter.py`

**Purpose:** Perform semantic interpretation with user-provided constraints

**Interface:**
```python
class ConstrainedSemanticInterpreter:
    async def interpret_with_constraints(
        self,
        embeddings: List[Dict[str, Any]],
        fact_pattern: Dict[str, Any],
        output_template: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Interpret embeddings using fact pattern constraints.
        
        Args:
            embeddings: Semantic embeddings from ArangoDB
            fact_pattern: User-provided fact pattern (entities, relationships, attributes)
            output_template: User-provided output structure template
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Interpreted data structured according to output template
        """
```

**Implementation:**
- Uses embeddings to reason about data
- Applies fact pattern to constrain reasoning (look for specific entities, relationships)
- Formats output according to template
- Stores results in GCS with lineage in Supabase

#### 4. Virtual Data Mapper

**Location:** `symphainy_platform/realms/insights/enabling_services/virtual_data_mapper.py`

**Purpose:** Create virtual data mappings without ingestion

**Interface:**
```python
class VirtualDataMapper:
    async def create_virtual_mapping(
        self,
        source_files: List[str],
        mapping_schema: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Create virtual data mapping (no ingestion).
        
        Args:
            source_files: List of file references
            mapping_schema: User-provided mapping schema
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Mapping result with virtual relationships
        """
```

**Implementation:**
- Uses semantic interpretation to understand source data
- Applies mapping schema to create virtual relationships
- Stores relationships in ArangoDB graph (no data ingestion)
- Tracks lineage in Supabase

---

## Updated Insights Realm Architecture

### Intent: `interpret_data_with_constraints`

**New Intent Type:**
```python
{
    "intent_type": "interpret_data_with_constraints",
    "parameters": {
        "parsed_file_id": "...",
        "fact_pattern_id": "...",  # User-provided fact pattern
        "output_template_id": "...",  # User-provided output template
        "reasoning_constraints": {...}  # Optional reasoning rules
    }
}
```

### Intent: `create_virtual_mapping`

**New Intent Type:**
```python
{
    "intent_type": "create_virtual_mapping",
    "parameters": {
        "source_files": ["file1", "file2", ...],
        "mapping_schema_id": "...",  # User-provided mapping schema
        "virtual": true
    }
}
```

---

## Data Model

### Fact Pattern Schema

```json
{
    "pattern_id": "uuid",
    "tenant_id": "uuid",
    "name": "PSO Permit Pattern",
    "version": "1.0",
    "entities": [
        {
            "name": "permit",
            "attributes": ["id", "type", "status"],
            "description": "Permit entity"
        }
    ],
    "relationships": [
        {
            "from": "permit",
            "to": "applicant",
            "type": "issued_to",
            "cardinality": "many-to-one"
        }
    ],
    "reasoning_rules": [
        {
            "rule": "If permit.status == 'active' AND permit.expiry_date < today, then flag as 'expiring_soon'"
        }
    ],
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

### Output Template Schema

```json
{
    "template_id": "uuid",
    "tenant_id": "uuid",
    "name": "PSO Permit Output Template",
    "version": "1.0",
    "structure": {
        "permit_id": "{{permit.id}}",
        "permit_type": "{{permit.type}}",
        "status": "{{permit.status}}",
        "applicant": {
            "name": "{{applicant.name}}",
            "contact": "{{applicant.contact}}"
        }
    },
    "validation_rules": [
        {
            "field": "permit_id",
            "required": true,
            "format": "string"
        }
    ],
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

### Mapping Schema Schema

```json
{
    "mapping_id": "uuid",
    "tenant_id": "uuid",
    "name": "Legacy to New System Mapping",
    "version": "1.0",
    "source_entities": ["policy", "claim"],
    "target_entities": ["policy_new", "claim_new"],
    "mappings": [
        {
            "source": "policy.policy_number",
            "target": "policy_new.external_id",
            "transformation": "prefix_with_legacy_",
            "validation": "required"
        }
    ],
    "relationships": [
        {
            "source": "policy -> claim",
            "target": "policy_new -> claim_new",
            "preserve": true
        }
    ],
    "virtual": true,
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

---

## Implementation Plan

### Phase 1: Core Infrastructure

1. **Fact Pattern Registry**
   - Create Supabase table: `fact_patterns`
   - Implement `FactPatternRegistry` class
   - Add CRUD operations

2. **Output Template Registry**
   - Create Supabase table: `output_templates`
   - Implement `OutputTemplateRegistry` class
   - Add CRUD operations

3. **Mapping Schema Registry**
   - Create Supabase table: `mapping_schemas`
   - Implement `MappingSchemaRegistry` class
   - Add CRUD operations

### Phase 2: Constrained Semantic Interpreter

4. **Constrained Semantic Interpreter**
   - Implement `ConstrainedSemanticInterpreter` class
   - Integrate with embeddings from ArangoDB
   - Apply fact pattern constraints
   - Format output according to template

5. **Update Insights Realm**
   - Add `interpret_data_with_constraints` intent
   - Route to `ConstrainedSemanticInterpreter`
   - Store results in GCS with lineage

### Phase 3: Virtual Data Mapper

6. **Virtual Data Mapper**
   - Implement `VirtualDataMapper` class
   - Create virtual relationships in ArangoDB graph
   - Track lineage in Supabase (no data ingestion)

7. **Update Insights Realm**
   - Add `create_virtual_mapping` intent
   - Route to `VirtualDataMapper`
   - Verify no data ingestion

### Phase 4: Platform SDK Integration

8. **Solution Builder Integration**
   - Add fact pattern registration to Solution Builder
   - Add output template registration to Solution Builder
   - Add mapping schema registration to Solution Builder

9. **Realm SDK Integration**
   - Add fact pattern support to Realm SDK
   - Add output template support to Realm SDK
   - Enable realms to use constraints

### Phase 5: E2E Testing

10. **E2E Tests**
    - Test PSO use case with fact pattern
    - Test AAR use case with fact pattern
    - Test data mapping with virtual pipeline
    - Verify composability (same engine, different constraints)

---

## Benefits

✅ **Composability:**
- Same semantic interpretation engine for all use cases
- Different constraints for different use cases
- No code changes needed for new use cases

✅ **Extensibility:**
- Users can define their own fact patterns
- Users can define their own output templates
- Users can define their own mapping schemas

✅ **Architectural Compliance:**
- Follows 5-layer architecture
- Uses Public Works pattern
- Follows Runtime Participation Contract

✅ **No Specialized Parsers:**
- Universal parsing (Content Realm)
- Universal semantic interpretation (Insights Realm)
- User-provided constraints (Platform SDK)

---

## Migration Path

### For Existing Use Cases

1. **PSO Use Case:**
   - Extract fact pattern from existing PSO parser
   - Create fact pattern in registry
   - Create output template in registry
   - Use `interpret_data_with_constraints` instead of specialized parser

2. **AAR Use Case:**
   - Extract fact pattern from existing AAR parser
   - Create fact pattern in registry
   - Create output template in registry
   - Use `interpret_data_with_constraints` instead of specialized parser

3. **Data Mapping:**
   - Extract mapping schema from existing data mash
   - Create mapping schema in registry
   - Use `create_virtual_mapping` instead of specialized data mash

---

## Success Criteria

✅ **Universal Engine:**
- Same semantic interpretation engine for all use cases
- No specialized parsers needed

✅ **User-Provided Constraints:**
- Users can define fact patterns
- Users can define output templates
- Users can define mapping schemas

✅ **Composability:**
- Same engine works for PSO, AAR, and any future use case
- No code changes needed for new use cases

✅ **Real Functionality:**
- All operations use real infrastructure
- All results stored with proper lineage
