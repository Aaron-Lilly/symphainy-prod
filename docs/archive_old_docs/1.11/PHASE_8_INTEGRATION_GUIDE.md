# Phase 8: Integration Guide

**Date:** January 10, 2026  
**Status:** 📋 **INTEGRATION READY**  
**Goal:** Integrate all parsing services with Platform Gateway and provide end-to-end usage

---

## ✅ Completed Components

### 1. Content Orchestrator ✅

**Location:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Features:**
- Routes parsing requests to appropriate parsing service
- Auto-detects parsing type from file extension
- Supports explicit parsing type override
- Integrates with all 4 parsing services

**Usage:**
```python
orchestrator = ContentOrchestrator(
    structured_service=structured_service,
    unstructured_service=unstructured_service,
    hybrid_service=hybrid_service,
    workflow_sop_service=workflow_sop_service,
    state_surface=state_surface
)

result = await orchestrator.parse_file(
    file_reference="file:tenant:session:file_id",
    filename="document.pdf",
    parsing_type="unstructured"  # Optional - auto-detected if not provided
)
```

---

## 📋 Integration Steps

### Step 1: Register Parsing Services with Curator

**Location:** Service initialization code

```python
from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService
from symphainy_platform.realms.content.services.structured_parsing_service import StructuredParsingService
from symphainy_platform.realms.content.services.unstructured_parsing_service import UnstructuredParsingService
from symphainy_platform.realms.content.services.hybrid_parsing_service import HybridParsingService
from symphainy_platform.realms.content.services.workflow_sop_parsing_service import WorkflowSOPParsingService

# Initialize services
structured_service = StructuredParsingService(state_surface, platform_gateway)
unstructured_service = UnstructuredParsingService(state_surface, platform_gateway)
hybrid_service = HybridParsingService(state_surface, platform_gateway)
workflow_sop_service = WorkflowSOPParsingService(state_surface, platform_gateway)

# Register with Curator
curator = CuratorFoundationService(public_works_foundation)
await curator.service_registry.register_service(
    service_instance=structured_service,
    service_metadata={
        "service_name": "structured_parsing_service",
        "realm": "content",
        "capabilities": ["parse_excel", "parse_csv", "parse_json", "parse_binary"]
    }
)

# Repeat for other services...
```

---

### Step 2: Register Parsing Abstractions with Public Works Foundation

**Location:** `symphainy_platform/foundations/public_works/foundation_service.py`

**Add to `_create_abstractions()` method:**

```python
async def _create_abstractions(self):
    """Create all infrastructure abstractions (Layer 1)."""
    self.logger.info("Creating infrastructure abstractions...")
    
    # Existing abstractions...
    self.state_abstraction = StateManagementAbstraction(...)
    self.service_discovery_abstraction = ServiceDiscoveryAbstraction(...)
    
    # Parsing abstractions
    from ..abstractions.pdf_processing_abstraction import PdfProcessingAbstraction
    from ..abstractions.word_processing_abstraction import WordProcessingAbstraction
    from ..abstractions.excel_processing_abstraction import ExcelProcessingAbstraction
    from ..abstractions.csv_processing_abstraction import CsvProcessingAbstraction
    from ..abstractions.json_processing_abstraction import JsonProcessingAbstraction
    from ..abstractions.text_processing_abstraction import TextProcessingAbstraction
    from ..abstractions.image_processing_abstraction import ImageProcessingAbstraction
    from ..abstractions.html_processing_abstraction import HtmlProcessingAbstraction
    from ..abstractions.kreuzberg_processing_abstraction import KreuzbergProcessingAbstraction
    from ..abstractions.mainframe_processing_abstraction import MainframeProcessingAbstraction
    
    # Create adapters first (when available)
    # pdf_adapter = PdfplumberAdapter()  # To be created/migrated
    # word_adapter = PythonDocxAdapter()  # To be created/migrated
    # etc.
    
    # Create abstractions
    self.pdf_processing_abstraction = PdfProcessingAbstraction(
        pdf_adapter=None,  # Will be set when adapter is available
        state_surface=self.state_surface  # Pass State Surface
    )
    
    # Repeat for other abstractions...
    
    self.logger.info("Parsing abstractions created")
```

**Add getter methods:**

```python
def get_pdf_processing_abstraction(self) -> Optional[Any]:
    """Get PDF processing abstraction."""
    return self.pdf_processing_abstraction

def get_word_processing_abstraction(self) -> Optional[Any]:
    """Get Word processing abstraction."""
    return self.word_processing_abstraction

# Repeat for other abstractions...
```

---

### Step 3: Create Platform Gateway (If Not Exists)

**Location:** `symphainy_platform/runtime/platform_gateway.py` (to be created)

**Purpose:** Provide unified access to abstractions and services

```python
"""
Platform Gateway

Provides unified access to abstractions and services across the platform.
"""

from typing import Dict, Any, Optional

class PlatformGateway:
    """Platform Gateway for accessing abstractions and services."""
    
    def __init__(
        self,
        public_works_foundation: Optional[Any] = None,
        curator: Optional[Any] = None
    ):
        self.public_works = public_works_foundation
        self.curator = curator
        self._abstraction_cache: Dict[str, Any] = {}
    
    async def get_abstraction(self, abstraction_name: str) -> Optional[Any]:
        """
        Get abstraction by name.
        
        Args:
            abstraction_name: Name of abstraction (e.g., "pdf_processing_abstraction")
        
        Returns:
            Abstraction instance or None
        """
        # Check cache
        if abstraction_name in self._abstraction_cache:
            return self._abstraction_cache[abstraction_name]
        
        # Get from Public Works Foundation
        if self.public_works:
            method_name = f"get_{abstraction_name}"
            if hasattr(self.public_works, method_name):
                abstraction = getattr(self.public_works, method_name)()
                if abstraction:
                    self._abstraction_cache[abstraction_name] = abstraction
                    return abstraction
        
        return None
    
    async def get_service(self, service_name: str) -> Optional[Any]:
        """
        Get service by name.
        
        Args:
            service_name: Name of service (e.g., "structured_parsing_service")
        
        Returns:
            Service instance or None
        """
        # Get from Curator service registry
        if self.curator:
            service_info = self.curator.service_registry.get_service(service_name)
            if service_info:
                return service_info.get("service_instance")
        
        return None
```

---

### Step 4: End-to-End Usage Example

**Complete workflow:**

```python
# 1. Initialize State Surface
from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService

public_works = PublicWorksFoundationService(config)
await public_works.initialize()

state_surface = StateSurface(
    state_abstraction=public_works.get_state_abstraction()
)

# 2. Store file in State Surface
file_data = b"..."
file_reference = await state_surface.store_file(
    session_id="session_123",
    tenant_id="tenant_456",
    file_data=file_data,
    filename="document.pdf"
)

# 3. Initialize Platform Gateway
from symphainy_platform.runtime.platform_gateway import PlatformGateway
from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService

curator = CuratorFoundationService(public_works)
platform_gateway = PlatformGateway(
    public_works_foundation=public_works,
    curator=curator
)

# 4. Initialize Parsing Services
from symphainy_platform.realms.content.services.structured_parsing_service import StructuredParsingService
from symphainy_platform.realms.content.services.unstructured_parsing_service import UnstructuredParsingService
from symphainy_platform.realms.content.services.hybrid_parsing_service import HybridParsingService
from symphainy_platform.realms.content.services.workflow_sop_parsing_service import WorkflowSOPParsingService

structured_service = StructuredParsingService(state_surface, platform_gateway)
unstructured_service = UnstructuredParsingService(state_surface, platform_gateway)
hybrid_service = HybridParsingService(state_surface, platform_gateway)
workflow_sop_service = WorkflowSOPParsingService(state_surface, platform_gateway)

# 5. Register services with Curator
await curator.service_registry.register_service(
    service_instance=structured_service,
    service_metadata={"service_name": "structured_parsing_service", "realm": "content"}
)
# Repeat for other services...

# 6. Initialize Content Orchestrator
from symphainy_platform.realms.content.orchestrators.content_orchestrator import ContentOrchestrator

orchestrator = ContentOrchestrator(
    structured_service=structured_service,
    unstructured_service=unstructured_service,
    hybrid_service=hybrid_service,
    workflow_sop_service=workflow_sop_service,
    state_surface=state_surface
)

# 7. Parse file
result = await orchestrator.parse_file(
    file_reference=file_reference,
    filename="document.pdf",
    parsing_type="unstructured"  # Optional
)

if result.success:
    print(f"Parsed {len(result.data.get('text_chunks', []))} text chunks")
else:
    print(f"Parsing failed: {result.error}")
```

---

## 🔗 Integration with Insights Pillar

### Validation Rules Flow

For mainframe/binary files, validation rules are extracted and can be used by Insights pillar:

```python
# Parse binary file with copybook
result = await orchestrator.parse_file(
    file_reference=file_reference,
    filename="data.bin",
    parsing_type="structured",
    options={
        "copybook_reference": copybook_reference
    }
)

# Validation rules are in result.validation_rules
if result.validation_rules:
    # Use with Insights pillar
    from symphainy_platform.realms.insights.services.data_quality_validation_service import DataQualityValidationService
    
    validation_service = DataQualityValidationService(...)
    validation_result = await validation_service.validate_binary_records(
        records=result.data.get("records", []),
        validation_rules=result.validation_rules
    )
```

---

## 📝 Testing Checklist

### Unit Tests
- [ ] Content Orchestrator routing logic
- [ ] Parsing type detection
- [ ] Service integration

### Integration Tests
- [ ] End-to-end parsing workflow
- [ ] State Surface integration
- [ ] Platform Gateway integration
- [ ] Validation rules extraction (mainframe)

### E2E Tests
- [ ] Full parsing pipeline
- [ ] Multiple file types
- [ ] Error handling
- [ ] Insights pillar integration

---

## 🔗 Related Documents

- `docs/PARSING_IMPLEMENTATION_STATUS.md` - Overall parsing status
- `docs/PHASE_6_PARSING_ABSTRACTIONS_COMPLETE.md` - Abstractions implementation
- `docs/PHASE_7_MAINFRAME_PARSING_COMPLETE.md` - Mainframe implementation
