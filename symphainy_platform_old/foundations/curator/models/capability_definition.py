"""
Capability Definition Model

Definition of a service capability for the Curator Foundation.

WHAT: A capability is something a service can do, defined by a protocol and contracts.
HOW: Capabilities are registered with Curator and discoverable by other services.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class CapabilityDefinition:
    """
    Definition of a service capability.
    
    A capability is something a service can do, defined by:
    - A unique name (capability_name)
    - A protocol that defines the contract (protocol_name)
    - One or more contracts (ways to invoke the capability - REQUIRED)
    - Semantic mapping (how it maps to domain/user concepts - optional)
    
    Contract Structure:
    Each contract can be one of:
    - "soa_api": {api_name, endpoint, method, handler, metadata}
    - "rest_api": {endpoint, method, handler, metadata}
    - "mcp_tool": {tool_name, tool_definition, metadata}
    
    Semantic Mapping Structure:
    {
        "domain_capability": "content.upload_file",  # Domain concept
        "semantic_api": "/api/v1/content-pillar/upload-file",  # User-facing API
        "user_journey": "upload_document_for_analysis"  # User journey step
    }
    """
    # Core identification
    capability_name: str  # Unique identifier (e.g., "file_parsing", "health_monitoring")
    service_name: str  # Which service provides this capability
    protocol_name: str  # Protocol class name (e.g., "NurseServiceProtocol", "FileParserProtocol")
    
    # Description
    description: str  # What this capability does
    realm: str  # Which realm this capability belongs to (smart_city, business_enablement, etc.)
    
    # Contracts (REQUIRED - capability must have at least one way to invoke it)
    contracts: Dict[str, Any]  # REQUIRED: At least one contract (soa_api, rest_api, mcp_tool)
    
    # Semantic mapping (optional but recommended for user-facing capabilities)
    semantic_mapping: Optional[Dict[str, Any]] = None
    
    # Inputs/Outputs/Determinism
    inputs: Optional[Dict[str, Any]] = None  # Input schema/description
    outputs: Optional[Dict[str, Any]] = None  # Output schema/description
    determinism: Optional[str] = None  # "deterministic", "non-deterministic", "conditional"
    
    # Versioning and metadata
    version: str = "1.0.0"
    registered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        """Validate and initialize capability definition."""
        # Validate contracts is not empty
        if not self.contracts:
            raise ValueError(f"Capability '{self.capability_name}' must have at least one contract (soa_api, rest_api, or mcp_tool)")
        
        # Validate at least one contract type is present
        contract_types = ["soa_api", "rest_api", "mcp_tool"]
        has_contract = any(contract_type in self.contracts for contract_type in contract_types)
        if not has_contract:
            raise ValueError(f"Capability '{self.capability_name}' must have at least one contract type: {', '.join(contract_types)}")
