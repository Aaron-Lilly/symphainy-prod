"""
Intent Model - Formal Intent Schema and Validation

Defines the formal structure for intents that flow through the Runtime.

WHAT (Runtime Role): I define what intents look like and how they're validated
HOW (Runtime Implementation): I provide intent schema, validation, and factory methods

Key Principle: Nothing executes without intent. Intent is the formal declaration
of what should happen, validated before execution begins.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from utilities import generate_event_id, get_clock, get_logger


class IntentType(str, Enum):
    """Canonical intent types."""
    # Content domain intents
    INGEST_FILE = "ingest_file"
    PARSE_CONTENT = "parse_content"
    EXTRACT_EMBEDDINGS = "extract_embeddings"
    ARCHIVE_FILE = "archive_file"
    DELETE_FILE = "delete_file"
    LIST_ARTIFACTS = "list_artifacts"
    GET_PARSED_FILE = "get_parsed_file"
    RETRIEVE_ARTIFACT_METADATA = "retrieve_artifact_metadata"
    
    # Insights domain intents
    ANALYZE_CONTENT = "analyze_content"
    INTERPRET_DATA = "interpret_data"
    MAP_RELATIONSHIPS = "map_relationships"
    
    # Journey domain intents (renamed from Operations)
    OPTIMIZE_PROCESS = "optimize_process"
    GENERATE_SOP = "generate_sop"
    CREATE_WORKFLOW = "create_workflow"
    ANALYZE_COEXISTENCE = "analyze_coexistence"
    CREATE_BLUEPRINT = "create_blueprint"
    
    # Outcomes domain intents
    SYNTHESIZE_OUTCOME = "synthesize_outcome"
    GENERATE_ROADMAP = "generate_roadmap"
    CREATE_POC = "create_poc"
    CREATE_SOLUTION = "create_solution"
    
    # Generic intents
    EXECUTE_WORKFLOW = "execute_workflow"
    QUERY_DATA = "query_data"


@dataclass
class Intent:
    """
    Formal intent structure.
    
    Intent is the formal declaration of what should happen.
    It must be validated before execution begins.
    """
    intent_id: str
    intent_type: str
    tenant_id: str
    session_id: str
    solution_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: get_clock().now_utc())
    idempotency_key: Optional[str] = None  # For preventing duplicate operations
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate intent structure.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate required fields
        if not self.intent_id:
            return False, "intent_id is required"
        
        if not self.intent_type:
            return False, "intent_type is required"
        
        if not self.tenant_id:
            return False, "tenant_id is required"
        
        if not self.session_id:
            return False, "session_id is required"
        
        if not self.solution_id:
            return False, "solution_id is required"
        
        # Validate intent_type is known
        try:
            IntentType(self.intent_type)
        except ValueError:
            # Allow custom intent types, but log warning
            pass
        
        # Validate parameters is a dict
        if not isinstance(self.parameters, dict):
            return False, "parameters must be a dictionary"
        
        # Validate metadata is a dict
        if not isinstance(self.metadata, dict):
            return False, "metadata must be a dictionary"
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert intent to dictionary."""
        return {
            "intent_id": self.intent_id,
            "intent_type": self.intent_type,
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
            "solution_id": self.solution_id,
            "parameters": self.parameters,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Intent":
        """Create intent from dictionary."""
        return cls(
            intent_id=data["intent_id"],
            intent_type=data["intent_type"],
            tenant_id=data["tenant_id"],
            session_id=data["session_id"],
            solution_id=data["solution_id"],
            parameters=data.get("parameters", {}),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", get_clock().now_utc().isoformat())),
        )


class IntentFactory:
    """
    Factory for creating intents.
    
    Provides convenience methods for creating common intent types.
    """
    
    @staticmethod
    def create_intent(
        intent_type: str,
        tenant_id: str,
        session_id: str,
        solution_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        intent_id: Optional[str] = None
    ) -> Intent:
        """
        Create an intent.
        
        Args:
            intent_type: Type of intent
            tenant_id: Tenant identifier
            session_id: Session identifier
            solution_id: Solution identifier
            parameters: Intent parameters
            metadata: Intent metadata
            intent_id: Optional intent ID (generated if not provided)
        
        Returns:
            Created intent
        """
        if intent_id is None:
            intent_id = generate_event_id()
        
        intent = Intent(
            intent_id=intent_id,
            intent_type=intent_type,
            tenant_id=tenant_id,
            session_id=session_id,
            solution_id=solution_id,
            parameters=parameters or {},
            metadata=metadata or {},
        )
        
        # Validate intent
        is_valid, error = intent.validate()
        if not is_valid:
            raise ValueError(f"Invalid intent: {error}")
        
        return intent
    
    @staticmethod
    def create_ingest_file_intent(
        tenant_id: str,
        session_id: str,
        solution_id: str,
        file_reference: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Intent:
        """Create ingest file intent."""
        return IntentFactory.create_intent(
            intent_type=IntentType.INGEST_FILE.value,
            tenant_id=tenant_id,
            session_id=session_id,
            solution_id=solution_id,
            parameters={"file_reference": file_reference},
            metadata=metadata or {},
        )
    
    @staticmethod
    def create_analyze_content_intent(
        tenant_id: str,
        session_id: str,
        solution_id: str,
        content_reference: str,
        analysis_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Intent:
        """Create analyze content intent."""
        return IntentFactory.create_intent(
            intent_type=IntentType.ANALYZE_CONTENT.value,
            tenant_id=tenant_id,
            session_id=session_id,
            solution_id=solution_id,
            parameters={
                "content_reference": content_reference,
                "analysis_type": analysis_type,
            },
            metadata=metadata or {},
        )
