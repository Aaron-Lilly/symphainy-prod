# Detailed Implementation Plan: Insurance Demo Readiness

**Date:** January 2026  
**Status:** 📋 **Ready for Execution**  
**Purpose:** Comprehensive, detailed implementation plan for insurance demo based on all answered questions

---

## Executive Summary

This plan provides **task-level detail** for implementing all features needed for the insurance demo, including:
- Complex policy rules extraction (investment allocation, cash value calculations, compliance)
- LLM adapter infrastructure (porting/rebuilding)
- Deterministic and semantic embeddings
- Frontend flow updates
- Comprehensive export functionality

**Timeline:** 6-8 weeks to demo-ready  
**Priority:** Foundation-first (minimize rework)

---

## Part 1: Foundation Infrastructure (Week 1-2)

### Task 1.1: Port/Build LLM Adapter Infrastructure 🔴 CRITICAL

**Status:** LLM adapters exist in `/symphainy_source/` but not in current codebase  
**Priority:** CRITICAL (blocks semantic embeddings)  
**Estimated Time:** 8-12 hours

#### Subtasks

**1.1.1: Port OpenAI Adapter** (3-4 hours)
- **Source:** `/symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/openai_adapter.py`
- **Target:** `/symphainy_source_code/symphainy_platform/foundations/public_works/adapters/openai_adapter.py`
- **Actions:**
  1. Copy adapter file
  2. Update imports to match current architecture
  3. Ensure ConfigAdapter pattern matches current implementation
  4. Test initialization with current Public Works Foundation
  5. Verify `generate_completion()` and `generate_embeddings()` methods work

**1.1.2: Port HuggingFace Adapter** (2-3 hours)
- **Source:** `/symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/huggingface_adapter.py`
- **Target:** `/symphainy_source_code/symphainy_platform/foundations/public_works/adapters/huggingface_adapter.py`
- **Actions:**
  1. Copy adapter file
  2. Update imports
  3. Ensure ConfigAdapter pattern matches
  4. Test `generate_embedding()` method
  5. Verify inference endpoint configuration

**1.1.3: Register Adapters in Public Works Foundation** (2-3 hours)
- **File:** `symphainy_platform/foundations/public_works_foundation/__init__.py` or initialization file
- **Actions:**
  1. Add adapter initialization in Public Works Foundation
  2. Expose via `get_llm_adapter()` and `get_huggingface_adapter()` methods
  3. Ensure ConfigAdapter is passed correctly
  4. Add error handling for missing configuration

**1.1.4: Create StatelessEmbeddingAgent** (3-4 hours)
- **File:** `symphainy_platform/civic_systems/agentic/agents/stateless_embedding_agent.py`
- **Actions:**
  1. Create StatelessEmbeddingAgent extending StatelessAgentBase
  2. Wrap HuggingFaceAdapter calls for governance
  3. Implement `generate_embedding()` method that:
     - Gets HuggingFaceAdapter from Public Works
     - Tracks usage (cost, metadata, audit)
     - Calls adapter with governance
     - Returns embedding vector
  4. Ensure lightweight pattern (no CrewAI overhead)
  5. Add error handling and retry logic

**1.1.5: Add LLM Access to AgentBase** (2-3 hours)
- **File:** `symphainy_platform/civic_systems/agentic/agent_base.py`
- **Actions:**
  1. Add `_call_llm()` method to AgentBase
  2. Implement governance (cost tracking, rate limiting, audit)
  3. Use Public Works to get LLM adapter
  4. Add metadata tracking (agent_id, agent_type, tenant_id)
  5. Add error handling and retry logic

**Implementation Pattern:**
```python
# StatelessEmbeddingAgent
class StatelessEmbeddingAgent(StatelessAgentBase):
    """Lightweight agent for embedding generation with governance."""
    
    async def generate_embedding(
        self,
        text: str,
        model: str = "sentence-transformers/all-mpnet-base-v2",
        context: ExecutionContext = None
    ) -> Dict[str, Any]:
        """Generate embedding via HuggingFaceAdapter with governance."""
        # Get HuggingFaceAdapter from Public Works
        hf_adapter = self.public_works.get_huggingface_adapter()
        
        # Track usage (governance)
        await self._track_usage(
            operation="embedding_generation",
            model=model,
            text_length=len(text),
            context=context
        )
        
        # Call adapter (with governance)
        result = await hf_adapter.generate_embedding(text, model)
        
        return result

# AgentBase._call_llm()
async def _call_llm(
    self,
    prompt: str,
    system_message: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 1000,
    temperature: float = 0.3,
    user_context: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Call LLM via agentic system (governed access)."""
    # Get LLM adapter from Public Works
    llm_adapter = self.public_works.get_llm_adapter()
    
    # Prepare request with governance metadata
    request = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    # Call via adapter (with governance)
    response = await llm_adapter.generate_completion(request)
    
    # Extract and return text
    return response["choices"][0]["message"]["content"]
```

**Acceptance Criteria:**
- ✅ OpenAI adapter accessible via Public Works
- ✅ HuggingFace adapter accessible via Public Works
- ✅ StatelessEmbeddingAgent created and registered
- ✅ Embedding generation goes through agent (governance)
- ✅ Agents can call `_call_llm()` method
- ✅ All external calls are tracked (cost, usage, metadata)
- ✅ Error handling works correctly

---

### Task 1.2: Implement Deterministic Embeddings 🔴 CRITICAL

**Status:** No implementation found - build from scratch  
**Priority:** CRITICAL (blocks schema matching)  
**Estimated Time:** 12-16 hours

#### Definition

**Deterministic Embeddings = Schema Fingerprints + Pattern Signatures**

- **Schema Fingerprint:** Hash of column structure (names, types, positions, constraints)
- **Pattern Signature:** Statistical signature of data patterns (value distributions, formats, ranges)
- **Purpose:** Enable exact schema matching and pattern validation

#### Subtasks

**1.2.1: Create DeterministicEmbeddingService** (6-8 hours)
- **File:** `symphainy_platform/realms/content/enabling_services/deterministic_embedding_service.py`
- **Actions:**
  1. Create service class following RealmServiceBase pattern
  2. Implement `create_deterministic_embeddings()` method
  3. Extract schema fingerprint:
     - Column names, types, positions
     - Constraints (not_null, unique, foreign_key)
     - Generate hash: `sha256(sorted_columns_with_types)`
  4. Extract pattern signature:
     - Value distributions (null_ratio, unique_ratio)
     - Value ranges (min, max, mean)
     - Format patterns (email, date, phone regex)
     - Sample values (first 10 non-null values)
  5. Store in ArangoDB (new collection: `deterministic_embeddings`)
  6. Link to parsed_file_id

**1.2.2: Add Intent Handler** (2-3 hours)
- **File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`
- **Actions:**
  1. Add `_handle_create_deterministic_embeddings()` method
  2. Accept `parsed_file_id` parameter
  3. Call DeterministicEmbeddingService
  4. Return deterministic_embedding_id and fingerprints

**1.2.3: Create Schema Matching Service** (4-5 hours)
- **File:** `symphainy_platform/realms/insights/enabling_services/schema_matching_service.py`
- **Actions:**
  1. Implement `validate_schema_match()` - exact match via fingerprints
  2. Implement `calculate_similarity_score()` - fuzzy match via pattern signatures
  3. Return mapping with confidence scores
  4. Identify gaps (unmapped source, unmapped target)

**Implementation Pattern:**
```python
class DeterministicEmbeddingService:
    async def create_deterministic_embeddings(
        self,
        parsed_file_id: str,
        parsed_content: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Create deterministic embeddings (schema fingerprints + pattern signatures)."""
        # Extract schema
        schema = parsed_content.get("metadata", {}).get("columns", [])
        
        # Create schema fingerprint
        schema_fingerprint = self._create_schema_fingerprint(schema)
        
        # Create pattern signature
        pattern_signature = await self._create_pattern_signature(
            parsed_content, schema
        )
        
        # Store in ArangoDB
        embedding_doc = {
            "parsed_file_id": parsed_file_id,
            "schema_fingerprint": schema_fingerprint,
            "pattern_signature": pattern_signature,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store and return
        embedding_id = await self._store_deterministic_embedding(embedding_doc)
        
        return {
            "deterministic_embedding_id": embedding_id,
            "schema_fingerprint": schema_fingerprint,
            "pattern_signature": pattern_signature
        }
```

**Acceptance Criteria:**
- ✅ Deterministic embeddings created from parsed files
- ✅ Schema fingerprints enable exact matching
- ✅ Pattern signatures enable similarity scoring
- ✅ Stored in ArangoDB with proper linking
- ✅ Intent handler works correctly

---

## Part 2: Semantic Embeddings & Interpretation (Week 2-3)

### Task 2.1: Implement Semantic Embedding Service 🔴 CRITICAL

**Status:** Placeholder exists - needs full implementation  
**Priority:** CRITICAL (blocks interpretation)  
**Estimated Time:** 10-14 hours

#### Subtasks

**2.1.1: Create EmbeddingService** (6-8 hours)
- **File:** `symphainy_platform/realms/content/enabling_services/embedding_service.py`
- **Reference:** Old implementation in `/symphainy_source/`
- **Actions:**
  1. Port/adapt from old implementation
  2. **CRITICAL:** Require `deterministic_embedding_id` as input (not `parsed_file_id`)
  3. Read deterministic embeddings from ArangoDB
  4. Use StatelessEmbeddingAgent for embeddings (governed access)
  5. Use agent for semantic meaning inference (via `_call_llm()`)
  6. Create 3 embeddings per column:
     - `metadata_embedding`: Column name + data type + structure
     - `meaning_embedding`: Semantic meaning (inferred via LLM)
     - `samples_embedding`: Representative sample values
  7. Representative sampling (every 10th row)
  8. Store via SemanticDataAbstraction (ArangoDB)
  9. Link to deterministic_embedding_id for traceability

**2.1.2: Update Content Orchestrator** (2-3 hours)
- **File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`
- **Actions:**
  1. Update `_handle_extract_embeddings()` to:
     - **Require `deterministic_embedding_id` parameter** (not `parsed_file_id`)
     - Validate deterministic embedding exists
     - Call EmbeddingService with deterministic_embedding_id
  2. Remove placeholder logic
  3. Add error handling (if deterministic embedding not found)
  4. Return real embedding_id and metadata

**2.1.3: Add Bulk Embedding Support** (2-3 hours)
- **File:** Same as above
- **Actions:**
  1. Update `_handle_bulk_extract_embeddings()` to use service
  2. Add parallel processing
  3. Add progress tracking
  4. Add error recovery

**Implementation Pattern:**
```python
class EmbeddingService:
    def __init__(self, public_works, ...):
        # StatelessEmbeddingAgent for embeddings (governed access)
        self.embedding_agent = agent_factory.create_agent(
            agent_type="stateless_embedding",
            public_works=public_works
        )
        
        # Agent for semantic meaning (LLM access via agent)
        self.semantic_meaning_agent = agent_factory.create_agent(
            agent_type="semantic_analysis",
            public_works=public_works
        )
    
    async def create_representative_embeddings(
        self,
        deterministic_embedding_id: str,  # ✅ REQUIRED - not parsed_file_id
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Create semantic embeddings from deterministic embeddings."""
        # 1. Get deterministic embeddings from ArangoDB
        deterministic_embeddings = await self._get_deterministic_embeddings(
            deterministic_embedding_id, context
        )
        
        # 2. Extract schema fingerprint and pattern signature
        schema_fingerprint = deterministic_embeddings["schema_fingerprint"]
        pattern_signature = deterministic_embeddings["pattern_signature"]
        
        # 3. Get parsed content (for sampling)
        parsed_file_id = deterministic_embeddings["parsed_file_id"]
        parsed_content = await self._get_parsed_content(parsed_file_id, context)
        
        # 4. Sample representative rows (every 10th)
        sampled_data = self._sample_representative(parsed_content, n=10)
        
        # 5. For each column, create 3 embeddings
        embeddings = []
        for column_info in schema_fingerprint["columns"]:
            column_name = column_info["name"]
            data_type = column_info["type"]
            samples = pattern_signature.get("sample_values", [])
            
            # Metadata embedding (via StatelessEmbeddingAgent - governed)
            metadata_embedding_result = await self.embedding_agent.generate_embedding(
                text=f"Column: {column_name}, Type: {data_type}",
                context=context
            )
            metadata_embedding = metadata_embedding_result.get("embedding", [])
            
            # Semantic meaning (via agent - governed LLM)
            semantic_meaning = await self.semantic_meaning_agent._call_llm(
                prompt=f"Infer semantic meaning: {column_name}, {data_type}, {samples}",
                system_message="You are a data analyst...",
                model="gpt-4o-mini"
            )
            
            # Meaning embedding (via StatelessEmbeddingAgent - governed)
            meaning_embedding_result = await self.embedding_agent.generate_embedding(
                text=semantic_meaning,
                context=context
            )
            meaning_embedding = meaning_embedding_result.get("embedding", [])
            
            # Samples embedding (via StatelessEmbeddingAgent - governed)
            samples_embedding_result = await self.embedding_agent.generate_embedding(
                text=f"Sample values: {', '.join(samples[:5])}",
                context=context
            )
            samples_embedding = samples_embedding_result.get("embedding", [])
            
            embeddings.append({
                "column_name": column_name,
                "metadata_embedding": metadata_embedding,
                "meaning_embedding": meaning_embedding,
                "samples_embedding": samples_embedding,
                "semantic_meaning": semantic_meaning,
                "sample_values": samples,
                "deterministic_embedding_id": deterministic_embedding_id  # Link
            })
        
        # 6. Store via SemanticDataAbstraction
        await self.semantic_data.store_semantic_embeddings(
            content_id=content_id,
            embeddings=embeddings,
            context=context
        )
        
        return {"embeddings_count": len(embeddings), "content_id": content_id}
```

**Acceptance Criteria:**
- ✅ Semantic embeddings created from deterministic embeddings (not parsed files)
- ✅ Requires deterministic_embedding_id as input
- ✅ 3 embeddings per column (metadata, meaning, samples)
- ✅ All embedding generation via StatelessEmbeddingAgent (governed)
- ✅ Semantic meaning inferred via agent (governed LLM)
- ✅ Stored in ArangoDB with link to deterministic_embedding_id
- ✅ Bulk operations work correctly

---

### Task 2.2: Implement Data Quality Assessment 🟡 HIGH

**Status:** Needs implementation  
**Priority:** HIGH (required for frontend flow)  
**Estimated Time:** 6-8 hours

#### Subtasks

**2.2.1: Create DataQualityAssessmentService** (4-5 hours)
- **File:** `symphainy_platform/realms/insights/enabling_services/data_quality_assessment_service.py`
- **Actions:**
  1. Implement `assess_data_quality()` method
  2. Calculate parsing confidence:
     - Record count vs expected
     - Field completeness
     - Data type validation
     - Format validation
  3. Calculate embedding confidence:
     - Schema fingerprint match quality
     - Pattern signature match quality
     - Missing fields detection
  4. Combine scores: `overall_confidence = (parsing_confidence + embedding_confidence) / 2`
  5. Identify issues:
     - Bad scan (parsing confidence < threshold)
     - Bad schema (embedding confidence < threshold)
     - Missing fields
     - Invalid data

**2.2.2: Add Intent Handler** (2-3 hours)
- **File:** `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`
- **Actions:**
  1. Add `_handle_assess_data_quality()` method
  2. Accept `parsed_file_id` and `deterministic_embedding_id`
  3. Call DataQualityAssessmentService
  4. Return quality scores and issues

**Acceptance Criteria:**
- ✅ Parsing confidence calculated
- ✅ Embedding confidence calculated
- ✅ Overall confidence score returned
- ✅ Issues identified and categorized
- ✅ Intent handler works correctly

---

## Part 3: Policy Rules Extraction (Week 3-4)

### Task 3.1: Implement Policy Rules Extraction Service 🔴 CRITICAL

**Status:** New requirement - complex rules extraction  
**Priority:** CRITICAL (core demo requirement)  
**Estimated Time:** 16-20 hours

#### Requirements (from Q9.1)

Extract complex rules for:
1. **Investment & Funding Rules:**
   - Sub-account allocations
   - Investment return logic
   - Funding flexibility

2. **Cash Value & Non-Forfeiture Rules:**
   - Calculation logic
   - Guaranteed minimums

3. **Riders, Features & Benefits:**
   - Death benefit options
   - No-lapse/guaranteed features
   - Persistency bonuses

4. **Policy Administration & Loans:**
   - Policy loan provisions
   - Lapse & grace periods
   - Premium offset/deductions

5. **Customer & Compliance Rules:**
   - Risk tolerance & suitability
   - Regulatory compliance (GDPR, CCPA, state laws)

#### Subtasks

**3.1.1: Create PolicyRulesExtractionService** (10-12 hours)
- **File:** `symphainy_platform/realms/insights/enabling_services/policy_rules_extraction_service.py`
- **Actions:**
  1. Implement `extract_policy_rules()` method
  2. Use semantic embeddings to identify rule patterns
  3. Use LLM (via agent) to extract structured rules from:
     - Policy documents (if parsed)
     - Data patterns (from embeddings)
     - Configuration files (if available)
  4. Structure rules into categories:
     ```python
     {
         "investment_rules": {
             "sub_account_allocations": [...],
             "investment_return_logic": {...},
             "funding_flexibility": {...}
         },
         "cash_value_rules": {
             "calculation_logic": {...},
             "guaranteed_minimums": {...}
         },
         "riders_features": {
             "death_benefit_options": [...],
             "no_lapse_features": {...},
             "persistency_bonuses": {...}
         },
         "administration_rules": {
             "loan_provisions": {...},
             "lapse_grace_periods": {...},
             "premium_deductions": {...}
         },
         "compliance_rules": {
             "risk_tolerance": {...},
             "regulatory_compliance": {...}
         }
     }
     ```
  5. Extract calculation formulas (if present in data)
  6. Extract business logic patterns

**3.1.2: Create Rule Pattern Recognition** (4-5 hours)
- **File:** Same as above
- **Actions:**
  1. Identify rule patterns in data:
     - Field names that indicate rules (e.g., "ALLOCATION_PERCENT", "INTEREST_RATE")
     - Value patterns that indicate rules (e.g., percentages, formulas)
     - Relationships between fields
  2. Use semantic embeddings to find similar patterns
  3. Use deterministic embeddings to validate schema matches

**3.1.3: Add LLM-Based Rule Extraction** (2-3 hours)
- **File:** Same as above
- **Actions:**
  1. Use agent to analyze policy data and extract rules
  2. Prompt engineering for rule extraction:
     ```python
     system_message = """You are an insurance policy rules extraction expert.
     Extract investment allocation rules, cash value calculation logic, riders,
     loan provisions, and compliance rules from the provided policy data."""
     
     prompt = f"""Analyze this policy data and extract all business rules:
     {policy_data}
     
     Return structured JSON with rule categories."""
     ```
  3. Parse LLM response into structured rules
  4. Validate extracted rules

**Acceptance Criteria:**
- ✅ Investment rules extracted
- ✅ Cash value rules extracted
- ✅ Riders/features extracted
- ✅ Administration rules extracted
- ✅ Compliance rules extracted
- ✅ Rules structured in JSON format
- ✅ Rules linked to source data

---

## Part 4: Target Data Model Matching (Week 4)

### Task 4.1: Implement Target Data Model Parsing 🟡 HIGH

**Status:** Needs implementation (anti-pattern fix)  
**Priority:** HIGH (blocks matching demo)  
**Estimated Time:** 8-12 hours

#### Subtasks

**4.1.1: Fix Frontend Flow** (4-6 hours)
- **Files:** Frontend code (separate repo)
- **Actions:**
  1. Remove target model upload from Insights tab
  2. Add file selector in Insights tab (from parsed files)
  3. Only show files with `parsing_type="data_model"`

**4.1.2: Add Data Model Parsing Type** (2-3 hours)
- **File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`
- **Actions:**
  1. Add `parsing_type="data_model"` support
  2. Route to appropriate parser based on file format:
     - Excel → Excel parser → JSON Schema converter
     - JSON → JSON Schema validator
     - SQL DDL → SQL parser → JSON Schema converter
     - CSV → Infer schema → JSON Schema converter

**4.1.3: Create DataModelParsingService** (2-3 hours)
- **File:** `symphainy_platform/realms/content/enabling_services/data_model_parsing_service.py`
- **Actions:**
  1. Implement `parse_to_json_schema()` method
  2. Support multiple input formats:
     - Excel (multi-tab) → JSON Schema
     - JSON Schema → Validate and return
     - SQL DDL → Parse and convert to JSON Schema
     - CSV → Infer schema and convert to JSON Schema
  3. Return JSON Schema format:
     ```json
     {
         "$schema": "http://json-schema.org/draft-07/schema#",
         "type": "object",
         "properties": {
             "field_name": {
                 "type": "string",
                 "description": "...",
                 "pattern": "...",
                 "required": true
             }
         }
     }
     ```

**Acceptance Criteria:**
- ✅ Target model uploaded in Content Pillar
- ✅ Parsed to JSON Schema
- ✅ Selectable in Insights tab
- ✅ Multiple formats supported (Excel, JSON, SQL, CSV)

---

### Task 4.2: Implement Source-to-Target Matching 🟡 HIGH

**Status:** Guided discovery exists but needs enhancement  
**Priority:** HIGH (core demo requirement)  
**Estimated Time:** 10-14 hours

#### Subtasks

**4.2.1: Enhance SchemaMatchingService** (4-5 hours)
- **File:** `symphainy_platform/realms/insights/enabling_services/schema_matching_service.py`
- **Actions:**
  1. Implement three-phase matching:
     - **Phase 1:** Schema alignment (exact match via fingerprints)
     - **Phase 2:** Semantic matching (fuzzy match via embeddings)
     - **Phase 3:** Pattern validation (data pattern compatibility)
  2. Return mapping with confidence scores
  3. Identify gaps (unmapped source, unmapped target)

**4.2.2: Create SemanticMatchingService** (3-4 hours)
- **File:** `symphainy_platform/realms/insights/enabling_services/semantic_matching_service.py`
- **Actions:**
  1. Use semantic embeddings to match columns by meaning
  2. Calculate similarity scores
  3. Suggest mappings based on semantic similarity

**4.2.3: Create PatternValidationService** (3-4 hours)
- **File:** `symphainy_platform/realms/insights/enabling_services/pattern_validation_service.py`
- **Actions:**
  1. Validate data patterns match expected patterns
  2. Check value ranges, formats, distributions
  3. Return validation results and warnings

**4.2.4: Integrate in GuidedDiscoveryService** (1-2 hours)
- **File:** `symphainy_platform/realms/insights/enabling_services/guided_discovery_service.py`
- **Actions:**
  1. Use all three matching services
  2. Combine results
  3. Return comprehensive mapping

**Acceptance Criteria:**
- ✅ Three-phase matching works
- ✅ Confidence scores calculated
- ✅ Gaps identified
- ✅ Mapping table generated
- ✅ Warnings/errors reported

---

## Part 5: Export to Migration Engine (Week 5)

### Task 5.1: Design Export Structure 🔴 CRITICAL

**Status:** Needs design based on Q9.1 and Q9.5  
**Priority:** CRITICAL (blocks handoff)  
**Estimated Time:** 4-6 hours (design) + 12-16 hours (implementation)

#### Export Content (Based on Q9.1)

**Recommended Export Structure:**
```json
{
    "export_metadata": {
        "export_date": "2026-01-XX",
        "source_system": "LEGACY-SYS-01",
        "target_system": "MODERN-PLATFORM",
        "total_policies": 100,
        "export_version": "1.0"
    },
    "data_mappings": {
        "field_mappings": [
            {
                "source_field": "POLICY_NUMBER",
                "target_field": "policy_number",
                "confidence": 0.98,
                "match_type": "exact",
                "transformation": null
            },
            {
                "source_field": "FACE_AMOUNT",
                "target_field": "face_amount",
                "confidence": 0.95,
                "match_type": "semantic",
                "transformation": "convert_to_decimal"
            }
        ],
        "unmapped_source_fields": [...],
        "unmapped_target_fields": [...]
    },
    "policy_rules": {
        "investment_rules": {
            "sub_account_allocations": [
                {
                    "policy_type": "VARIABLE_LIFE",
                    "allocation_rules": {
                        "stock_fund": {"min": 0, "max": 100, "default": 60},
                        "bond_fund": {"min": 0, "max": 100, "default": 30},
                        "money_market": {"min": 0, "max": 100, "default": 10}
                    },
                    "rebalancing_rules": {
                        "frequency": "quarterly",
                        "threshold": 5
                    }
                }
            ],
            "investment_return_logic": {
                "assumed_rate": 0.05,
                "calculation_method": "daily_valuation"
            },
            "funding_flexibility": {
                "premium_types": ["fixed", "flexible"],
                "minimum_premium": 100.00,
                "maximum_premium": 10000.00
            }
        },
        "cash_value_rules": {
            "calculation_logic": {
                "method": "net_cash_surrender_value",
                "formula": "cash_value = premium_paid - fees - loans + interest",
                "interest_rate": "variable"
            },
            "guaranteed_minimums": {
                "minimum_interest_rate": 0.02,
                "minimum_death_benefit": "face_amount"
            }
        },
        "riders_features": {
            "death_benefit_options": [
                {"option": "A", "description": "Level death benefit"},
                {"option": "B", "description": "Increasing death benefit"}
            ],
            "no_lapse_features": {
                "available": true,
                "duration_years": [1, 3, 5],
                "activation_conditions": "premium_paid >= minimum"
            },
            "persistency_bonuses": {
                "available": true,
                "enhancement_amount": "percentage_of_cash_value",
                "duration": "lifetime"
            }
        },
        "administration_rules": {
            "loan_provisions": {
                "available": true,
                "interest_rate": "variable",
                "loan_value_limit": "percentage_of_cash_value",
                "maximum_loan_percentage": 0.90
            },
            "lapse_grace_periods": {
                "grace_period_days": 31,
                "reinstatement_period_days": 365
            },
            "premium_deductions": {
                "mortality_expense_charge": "percentage_of_account_value",
                "administrative_fee": "flat_rate",
                "premium_load": "percentage_of_premium"
            }
        },
        "compliance_rules": {
            "risk_tolerance": {
                "extraction_method": "from_application_data",
                "fields": ["age", "income", "risk_profile"]
            },
            "regulatory_compliance": {
                "data_privacy": ["GDPR", "CCPA"],
                "state_regulations": ["ARIZONA_VARIABLE_LIFE_REGS"],
                "federal_regulations": ["SEC_RULE_151A"]
            }
        }
    },
    "transformation_rules": [
        {
            "source_field": "FACE_AMOUNT",
            "target_field": "face_amount",
            "transformation": "convert_to_decimal",
            "parameters": {"precision": 2}
        },
        {
            "source_field": "POLICY_TYPE",
            "target_field": "policy_type",
            "transformation": "normalize_enum",
            "parameters": {"mapping": {"LIFE": "life", "TERM": "term"}}
        }
    ],
    "validation_rules": [
        {
            "field": "policy_number",
            "rule": "required",
            "message": "Policy number is required"
        },
        {
            "field": "face_amount",
            "rule": "range",
            "parameters": {"min": 0, "max": 10000000},
            "message": "Face amount must be between 0 and 10,000,000"
        }
    ],
    "data_relationships": [
        {
            "source_table": "POLICY_MASTER",
            "target_table": "policies",
            "relationship_type": "one_to_one",
            "key_fields": ["POLICY_NUMBER", "policy_number"]
        },
        {
            "source_table": "CLAIM",
            "target_table": "claims",
            "relationship_type": "one_to_many",
            "key_fields": ["POLICY_NUMBER", "policy_id"]
        }
    ],
    "staged_data": {
        "format": "jsonl",
        "sample_records": [
            {"policy_number": "POL000001", "face_amount": 500000, ...},
            {"policy_number": "POL000002", "face_amount": 750000, ...}
        ]
    },
    "security_metadata": {
        "encryption": "AES-256",
        "access_controls": ["role_based"],
        "data_classification": "confidential"
    }
}
```

#### Subtasks

**5.1.1: Create ExportService** (8-10 hours)
- **File:** `symphainy_platform/realms/outcomes/enabling_services/export_service.py`
- **Actions:**
  1. Implement `export_to_migration_engine()` method
  2. Collect all required data:
     - Data mappings (from matching service)
     - Policy rules (from extraction service)
     - Transformation rules (from matching service)
     - Validation rules (from data quality service)
     - Data relationships (from schema analysis)
     - Staged data (from parsed content)
  3. Structure export according to design
  4. Support multiple formats (JSON, YAML, SQL, CSV)

**5.1.2: Add Export Intent** (2-3 hours)
- **File:** `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py`
- **Actions:**
  1. Add `_handle_export_to_migration_engine()` method
  2. Accept parameters:
     - `solution_id` (required)
     - `export_format` (required: "json", "yaml", "sql", "csv")
     - `include_mappings` (optional, default: true)
     - `include_rules` (optional, default: true)
     - `include_staged_data` (optional, default: false)
  3. Call ExportService
  4. Return export artifact (downloadable)

**5.1.3: Add File Export Support** (2-3 hours)
- **File:** Same as above
- **Actions:**
  1. Format export data based on format parameter
  2. Store as artifact in Artifact Plane
  3. Return download URL or file reference

**Acceptance Criteria:**
- ✅ Export includes all required sections
- ✅ Policy rules extracted and included
- ✅ Data mappings included
- ✅ Transformation rules included
- ✅ Multiple formats supported
- ✅ Export artifact downloadable

---

## Part 6: Frontend Flow Updates (Week 5-6)

### Task 6.1: Update Content Pillar UI (Data Mash) 🟡 HIGH

**Status:** Data Mash exists - needs deterministic embeddings step added  
**Priority:** HIGH (user experience)  
**Estimated Time:** 4-6 hours (frontend work)

#### Subtasks

**6.1.1: Add Deterministic Embeddings Step to Data Mash** (2-3 hours)
- **Location:** Content Pillar UI - Data Mash component
- **File:** `symphainy-frontend/app/(protected)/pillars/content/components/DataMash.tsx`
- **Actions:**
  1. Add new step between "Select Parsed File" and "Create Embeddings"
  2. Step 1.5: "Create Deterministic Embeddings"
  3. Add dropdown to select parsed file (if not already selected)
  4. Add "Create Deterministic Embeddings" button
  5. Call `create_deterministic_embeddings` intent
  6. Show progress and results
  7. Store `deterministic_embedding_id` in state

**6.1.2: Update Semantic Embeddings Step** (1-2 hours)
- **Location:** Same file - Data Mash component
- **Actions:**
  1. Update "Step 2: Create Embeddings" to:
     - Require deterministic_embedding_id (show error if not created)
     - Add dropdown to select deterministic embedding (if multiple exist)
     - Update `extract_embeddings` call to pass `deterministic_embedding_id` (not `parsed_file_id`)
  2. Show validation message if deterministic embeddings not created
  3. Update button text/labels for clarity

**6.1.3: Add Target Model Upload** (1-2 hours)
- **Location:** Content Pillar UI (separate from Data Mash)
- **Actions:**
  1. Add file upload for target data model
  2. Specify `parsing_type="data_model"` on upload
  3. Show parsed JSON Schema after parsing
  4. Mark file as "Data Model" type

**Updated Data Mash Flow:**
```
Step 1: Select Parsed File (existing)
Step 1.5: Create Deterministic Embeddings (NEW)
  - Select parsed file (if not already selected)
  - Click "Create Deterministic Embeddings"
  - Wait for completion
  - Store deterministic_embedding_id
Step 2: Create Semantic Embeddings (UPDATED)
  - Requires deterministic_embedding_id
  - Select deterministic embedding (if multiple)
  - Click "Create Embeddings"
  - Pass deterministic_embedding_id to intent
```

**Acceptance Criteria:**
- ✅ Deterministic embeddings step added to Data Mash
- ✅ Semantic embeddings requires deterministic_embedding_id
- ✅ Flow is clear and sequential
- ✅ Target model upload works (separate from Data Mash)
- ✅ Files marked correctly

---

### Task 6.2: Update Insights Pillar UI 🟡 HIGH

**Status:** Needs updates based on Q9.3  
**Priority:** HIGH (user experience)  
**Estimated Time:** 6-8 hours (frontend work)

#### Subtasks

**6.2.1: Add Data Quality Assessment** (2-3 hours)
- **Location:** Insights Pillar UI
- **Actions:**
  1. Add section to show data quality scores
  2. Display parsing confidence + embedding confidence
  3. Show overall confidence score
  4. Display issues (bad scan, bad schema)
  5. Call `assess_data_quality` intent

**6.2.2: Update Target Model Selection** (2-3 hours)
- **Location:** Insights Pillar UI
- **Actions:**
  1. Remove upload functionality
  2. Add file selector (dropdown) showing parsed data models
  3. Filter to show only `parsing_type="data_model"` files
  4. Allow selection of target model

**6.2.3: Add Interpretation Flow** (2-3 hours)
- **Location:** Insights Pillar UI
- **Actions:**
  1. After selecting target model, show "Interpret Data" button
  2. Call `interpret_data` intent with `guide_id` (target model)
  3. Show mapping table with confidence scores
  4. Show gaps and warnings

**Acceptance Criteria:**
- ✅ Data quality assessment displayed
- ✅ Target model selector works
- ✅ Interpretation flow works
- ✅ Mapping table displayed

---

### Task 6.3: Add Export Section 🟡 HIGH

**Status:** New requirement  
**Priority:** HIGH (demo requirement)  
**Estimated Time:** 4-6 hours (frontend work)

#### Subtasks

**6.3.1: Add Export Tab/Section** (2-3 hours)
- **Location:** Outcomes Pillar UI (or new Export section)
- **Actions:**
  1. Add export section after solution creation
  2. Show solution selector
  3. Add format selector (JSON, YAML, SQL, CSV)
  4. Add "Export" button

**6.3.2: Add Export Preview** (2-3 hours)
- **Location:** Same as above
- **Actions:**
  1. Show export preview (mapping table, rules summary)
  2. Show download button
  3. Display export metadata

**Acceptance Criteria:**
- ✅ Export section accessible
- ✅ Format selector works
- ✅ Export preview shows
- ✅ Download works

---

## Part 7: Testing & Validation (Week 6)

### Task 7.1: Insurance Demo Test Suite ✅ COMPLETE

**Status:** Created - needs execution  
**Priority:** HIGH  
**Estimated Time:** 4-6 hours (execution + fixes)

#### Subtasks

**7.1.1: Run Existing Tests** (2-3 hours)
- **File:** `tests/integration/capabilities/insurance_demo/test_insurance_policy_parsing.py`
- **Actions:**
  1. Run comprehensive parsing test
  2. Run data quality test
  3. Run edge case test
  4. Fix any issues found

**7.1.2: Add Integration Tests** (2-3 hours)
- **Files:** New test files
- **Actions:**
  1. Test end-to-end flow:
     - Upload → Parse → Deterministic Embeddings → Semantic Embeddings
     - Data Quality Assessment
     - Target Model Matching
     - Policy Rules Extraction
     - Export
  2. Test with comprehensive test data
  3. Validate all outputs

**Acceptance Criteria:**
- ✅ All tests pass
- ✅ End-to-end flow works
- ✅ All features validated

---

## Part 8: Timeline & Dependencies

### Week 1-2: Foundation
- **Task 1.1:** LLM Adapter Infrastructure (10-15h) - Added StatelessEmbeddingAgent
- **Task 1.2:** Deterministic Embeddings (12-16h)
- **Total:** 22-31 hours

### Week 2-3: Semantic Embeddings
- **Task 2.1:** Semantic Embedding Service (10-14h)
- **Task 2.2:** Data Quality Assessment (6-8h)
- **Total:** 16-22 hours

### Week 3-4: Policy Rules & Matching
- **Task 3.1:** Policy Rules Extraction (16-20h)
- **Task 4.1:** Target Data Model Parsing (8-12h)
- **Task 4.2:** Source-to-Target Matching (10-14h)
- **Total:** 34-46 hours

### Week 5: Export & Frontend
- **Task 5.1:** Export to Migration Engine (16-22h)
- **Task 6.1:** Content Pillar UI (Data Mash updates) (4-6h) - Reduced, already exists
- **Task 6.2:** Insights Pillar UI (6-8h)
- **Task 6.3:** Export Section (4-6h)
- **Total:** 30-42 hours

### Week 6: Testing
- **Task 7.1:** Test Suite Execution (4-6h)
- **Buffer:** 10-15 hours for fixes
- **Total:** 14-21 hours

### **Grand Total:** 118-163 hours (14.75-20.4 days)

**Note:** Time estimates updated to reflect:
- StatelessEmbeddingAgent creation (+2-3 hours)
- Data Mash updates (reduced from 6-8h to 4-6h since component exists)

---

## Part 9: Critical Dependencies

### Must Complete First
1. **LLM Adapter Infrastructure** (Task 1.1)
   - Blocks: Semantic Embeddings (Task 2.1) - Needs StatelessEmbeddingAgent
   - Blocks: Policy Rules Extraction (Task 3.1)

2. **Deterministic Embeddings** (Task 1.2)
   - Blocks: Semantic Embeddings (Task 2.1) - **CRITICAL:** Required as input
   - Blocks: Data Quality Assessment (Task 2.2)
   - Blocks: Source-to-Target Matching (Task 4.2)

3. **Semantic Embeddings** (Task 2.1)
   - Blocks: Policy Rules Extraction (Task 3.1)
   - Blocks: Source-to-Target Matching (Task 4.2)
   - **Requires:** Deterministic Embeddings (Task 1.2) - Must complete first

### Can Work in Parallel
- Frontend updates (Task 6.x) can be done in parallel with backend
- Testing (Task 7.1) can start as features complete

---

## Part 10: Risk Mitigation

### High-Risk Items

1. **Policy Rules Extraction Complexity**
   - **Risk:** Rules may not be extractable from data alone
   - **Mitigation:** Use LLM to infer rules, accept "best effort" for demo
   - **Fallback:** Pre-populate common rules, allow manual override

2. **LLM Adapter Porting**
   - **Risk:** Adapters may not work with current architecture
   - **Mitigation:** Test early, rebuild if needed
   - **Fallback:** Build new adapters from scratch

3. **Frontend Flow Changes**
   - **Risk:** Frontend may be in separate repo, coordination needed
   - **Mitigation:** Document API contracts clearly, coordinate early
   - **Fallback:** Use API-only approach, frontend can catch up

---

## Part 11: Success Criteria

### Demo Readiness Checklist

- ✅ Mainframe binary files parse correctly
- ✅ Deterministic embeddings created
- ✅ Semantic embeddings created
- ✅ Data quality assessed
- ✅ Target data model parsed
- ✅ Source-to-target matching works
- ✅ Policy rules extracted
- ✅ Export generated with all required sections
- ✅ Frontend flow works end-to-end
- ✅ All tests pass

---

**Last Updated:** January 2026  
**Status:** Ready for execution
