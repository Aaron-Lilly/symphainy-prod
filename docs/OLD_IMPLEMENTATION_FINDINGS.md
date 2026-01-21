# Old Implementation Findings

**Date:** January 2026  
**Status:** 📋 **Investigation Complete**  
**Purpose:** Document findings from searching old implementation for deterministic embeddings and LLM adapters

---

## Executive Summary

Searched `/symphainy_source/` and current codebase for:
1. Deterministic embedding implementation
2. LLM adapter infrastructure
3. Agent LLM access patterns

**Key Findings:**
- ❌ **No deterministic embedding implementation found** in old codebase
- ✅ **OpenAI adapter exists** in old codebase (`/symphainy_source/`)
- ❌ **No LLM adapters** in current codebase public_works/adapters
- ❌ **No `_call_llm()` method** in current AgentBase

---

## Part 1: Deterministic Embeddings Search

### Search Strategy
- Searched for: `deterministic embedding`, `schema fingerprint`, `pattern signature`, `column hash`
- Locations: `/symphainy_source/` entire directory
- Results: **No implementation found**

### What Was Found
- **Pattern matching code** (in antipattern detection service) - uses hash for violation IDs, not schema fingerprints
- **Method signature alignment** patterns (documentation) - not related to embeddings
- **No deterministic embedding service** or implementation

### Conclusion
**Deterministic embeddings need to be built from scratch** based on the recommended definition:
- Schema fingerprints (hash of column structure)
- Pattern signatures (statistical data patterns)

---

## Part 2: LLM Adapter Infrastructure

### Old Codebase (`/symphainy_source/`)

#### ✅ OpenAI Adapter Found
**Location:** `/symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/openai_adapter.py`

**Key Features:**
- `generate_completion()` - Chat completions
- `generate_embeddings()` - Embedding generation
- `get_models()` - Model listing
- `is_model_available()` - Model availability check
- Uses `AsyncOpenAI` client
- ConfigAdapter-based initialization

**Structure:**
```python
class OpenAIAdapter:
    def __init__(self, api_key: str = None, base_url: str = None, config_adapter = None):
        # Initializes AsyncOpenAI client
    
    async def generate_completion(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Generates chat completion
    
    async def generate_embeddings(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        # Generates embeddings
```

#### ✅ HuggingFace Adapter Found
**Location:** `/symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/huggingface_adapter.py`

**Key Features:**
- `generate_embedding()` - Embedding generation
- `inference()` - General inference endpoint calls
- Uses HuggingFace Inference Endpoints
- ConfigAdapter-based initialization

**Structure:**
```python
class HuggingFaceAdapter:
    def __init__(self, endpoint_url: str = None, api_key: str = None, config_adapter = None):
        # Initializes HuggingFace client
    
    async def generate_embedding(self, text: str, model: str = "sentence-transformers/all-mpnet-base-v2") -> Dict[str, Any]:
        # Generates embeddings via inference endpoint
```

### Current Codebase (`/symphainy_source_code/`)

#### ❌ No LLM Adapters in Public Works
**Location Checked:** `/symphainy_source_code/symphainy_platform/foundations/public_works/adapters/`

**Found Adapters:**
- `arango_adapter.py`
- `excel_adapter.py`
- `gcs_adapter.py`
- `json_adapter.py`
- `mainframe_parsing/`
- `pdf_adapter.py`
- `redis_adapter.py`
- `supabase_adapter.py`
- ... (no `openai_adapter.py` or `huggingface_adapter.py`)

**Conclusion:** LLM adapters need to be ported from old codebase or created new.

---

## Part 3: Agent LLM Access Patterns

### Current AgentBase

**Location:** `/symphainy_source_code/symphainy_platform/civic_systems/agentic/agent_base.py`

**Methods Found:**
- `use_tool()` - Tool usage (placeholder)
- `get_session_state()` - Session state retrieval
- `request_contribution()` - Agent collaboration
- `process_contribution_request()` - Process collaboration requests
- `validate_output()` - Output validation

**Missing:**
- ❌ `_call_llm()` method
- ❌ LLM adapter access
- ❌ LLM call tracking/governance

### Agent Implementation Pattern

**Found in:** `stateless_agent.py`, `workflow_optimization_agent.py`, etc.

**Pattern:**
- Agents have `generate_*` methods (e.g., `generate_semantic_meaning()`, `generate_suggestions()`)
- These methods are abstract/placeholder
- No direct LLM access pattern found

**Example:**
```python
class StatelessAgentBase(AgentBase):
    async def generate_semantic_meaning(
        self,
        data: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        # Default implementation: Return data structure
        return {
            "data_structure": type(data).__name__,
            "keys": list(data.keys()) if isinstance(data, dict) else [],
            "semantic_type": "unknown"
        }
```

**Conclusion:** Agents need `_call_llm()` method added to AgentBase for governed LLM access.

---

## Part 4: Old Embedding Service Implementation

### Found: EmbeddingService in Old Codebase

**Location:** `/symphainy_source/symphainy-platform/backend/content/services/embedding_service/embedding_service.py`

**Key Features:**
- Uses `HuggingFaceAdapter` for embeddings (direct access)
- Uses `StatelessHFInferenceAgent` for semantic meaning (via agent)
- Creates 3 embeddings per column:
  1. `metadata_embedding` - Column name + data type + structure
  2. `meaning_embedding` - Semantic meaning (inferred via LLM)
  3. `samples_embedding` - Representative sample values
- Stores via `SemanticDataAbstraction` (ArangoDB)
- Representative sampling (every 10th row)

**LLM Access Pattern:**
```python
# In embedding_creation.py
async def _infer_semantic_meaning(self, column_name, data_type, sample_values):
    # Uses agent's _call_llm_simple method
    response_text = await self.service.semantic_meaning_agent._call_llm_simple(
        prompt=user_prompt,
        system_message=system_message,
        model="gpt-4o-mini",
        max_tokens=30,
        temperature=0.3,
        user_context=None,
        metadata={"task": "infer_semantic_meaning", "column": column_name}
    )
```

**Critical Finding:** Old implementation uses `_call_llm_simple()` method on agents, which doesn't exist in current AgentBase.

---

## Part 5: Recommendations

### 1. Port LLM Adapters from Old Codebase

**Action:** Copy and adapt:
- `openai_adapter.py` → `/symphainy_source_code/symphainy_platform/foundations/public_works/adapters/openai_adapter.py`
- `huggingface_adapter.py` → `/symphainy_source_code/symphainy_platform/foundations/public_works/adapters/huggingface_adapter.py`

**Adaptations Needed:**
- Update imports to match current architecture
- Ensure ConfigAdapter pattern matches current implementation
- Add to Public Works Foundation initialization

**Estimated Time:** 2-4 hours

---

### 2. Add LLM Access to AgentBase

**Action:** Add `_call_llm()` method to `AgentBase`

**Implementation:**
```python
# In agent_base.py
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
    """
    Call LLM via agentic system (governed access).
    
    This ensures:
    - Cost tracking
    - Rate limiting
    - Audit trail
    - Policy enforcement
    """
    # Get LLM adapter from Public Works
    if not hasattr(self, 'public_works') or not self.public_works:
        raise ValueError("Public Works not available - cannot access LLM adapter")
    
    llm_adapter = self.public_works.get_llm_adapter()
    if not llm_adapter:
        raise ValueError("LLM adapter not available")
    
    # Prepare request
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
    
    # Extract text from response
    if response.get("error"):
        raise RuntimeError(f"LLM call failed: {response['error']}")
    
    choices = response.get("choices", [])
    if not choices:
        raise RuntimeError("LLM call returned no choices")
    
    return choices[0]["message"]["content"]
```

**Estimated Time:** 2-3 hours

---

### 3. Build Deterministic Embeddings from Scratch

**Action:** Implement based on recommended definition (see main recommendations document)

**Components Needed:**
- `DeterministicEmbeddingService` - Creates schema fingerprints + pattern signatures
- `SchemaMatchingService` - Matches schemas using fingerprints
- `PatternValidationService` - Validates data patterns

**Estimated Time:** 12-16 hours

---

## Part 6: Summary

### What Exists
- ✅ OpenAI adapter in old codebase (can be ported)
- ✅ HuggingFace adapter in old codebase (can be ported)
- ✅ Embedding service pattern in old codebase (can be adapted)
- ✅ Agent structure in current codebase (needs LLM access method)

### What's Missing
- ❌ LLM adapters in current codebase
- ❌ `_call_llm()` method in AgentBase
- ❌ Deterministic embedding implementation (old or new)
- ❌ LLM adapter registration in Public Works Foundation

### Next Steps
1. Port LLM adapters from old codebase (2-4 hours)
2. Add `_call_llm()` to AgentBase (2-3 hours)
3. Register adapters in Public Works Foundation (1-2 hours)
4. Build deterministic embeddings from scratch (12-16 hours)

**Total Estimated Time:** 17-25 hours

---

**Last Updated:** January 2026
