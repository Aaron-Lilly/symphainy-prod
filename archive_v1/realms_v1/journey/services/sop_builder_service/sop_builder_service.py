"""
SOP Builder Service

Deterministic service for creating Standard Operating Procedures.
Uses State Surface for state storage (wizard sessions).
Stores SOP artifacts in GCS with references in State Surface.

WHAT (Journey Realm): I create Standard Operating Procedures
HOW (Service): I provide deterministic SOP creation, validation, and wizard management
"""

import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from utilities import get_logger, get_clock

logger = get_logger(__name__)


class SOPBuilderService:
    """
    SOP Builder Service.
    
    Provides deterministic SOP creation capabilities:
    - Create SOPs from structured data
    - Validate SOP structure
    - Wizard pattern for interactive SOP creation
    
    Pattern:
    - Deterministic
    - Stateless (uses State Surface for state)
    - Input → Output
    - No orchestration
    - No reasoning
    """
    
    def __init__(
        self,
        state_surface: Any,
        file_storage_abstraction: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize SOP Builder Service.
        
        Args:
            state_surface: State Surface instance for state storage
            file_storage_abstraction: File Storage Abstraction for artifact storage
            platform_gateway: Platform Gateway for accessing abstractions
        """
        self.state_surface = state_surface
        self.file_storage = file_storage_abstraction
        self.platform_gateway = platform_gateway
        self.logger = logger
        self.clock = get_clock()
        
        # SOP templates
        self.sop_templates = {
            "standard": {
                "sections": ["purpose", "scope", "responsibilities", "procedures", "quality_control", "references"],
                "required_fields": ["title", "purpose", "procedures"]
            },
            "technical": {
                "sections": ["overview", "prerequisites", "step_by_step", "troubleshooting", "maintenance"],
                "required_fields": ["title", "overview", "step_by_step"]
            },
            "administrative": {
                "sections": ["policy", "procedures", "forms", "approvals", "review_cycle"],
                "required_fields": ["title", "policy", "procedures"]
            }
        }
        
        self.logger.info("✅ SOP Builder Service initialized")
    
    async def start_wizard_session(
        self,
        session_id: str,
        tenant_id: str,
        initial_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a new SOP wizard session.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
            initial_description: Optional initial process description
        
        Returns:
            Dict with wizard_session_token and wizard_state
        """
        try:
            self.logger.info(f"🧙 Starting SOP wizard session for tenant: {tenant_id}, session: {session_id}")
            
            # Generate session token
            session_token = f"wizard_{uuid.uuid4().hex[:16]}"
            
            # Initialize wizard state
            wizard_state = {
                "session_token": session_token,
                "current_step": 1,
                "total_steps": 5,
                "progress_percentage": 0.0,
                "sop_data": {},
                "next_question": "What type of SOP do you want to create? (standard, technical, or administrative)",
                "initial_description": initial_description,
                "created_at": self.clock.now_iso()
            }
            
            # Store wizard session in State Surface
            await self.state_surface.set_session_state(
                session_id=f"{session_id}:{session_token}",
                tenant_id=tenant_id,
                state=wizard_state
            )
            
            self.logger.info(f"✅ Wizard session started: {session_token}")
            
            return {
                "success": True,
                "session_token": session_token,
                "wizard_state": wizard_state
            }
        
        except Exception as e:
            self.logger.error(f"Failed to start wizard session: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_wizard_step(
        self,
        session_id: str,
        tenant_id: str,
        session_token: str,
        step_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process wizard step.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
            session_token: Wizard session token
            step_data: Step data from user
        
        Returns:
            Dict with step result and updated wizard state
        """
        try:
            self.logger.info(f"Processing wizard step for session: {session_token}")
            
            # Get wizard session from State Surface
            wizard_state = await self.state_surface.get_session_state(
                session_id=f"{session_id}:{session_token}",
                tenant_id=tenant_id
            )
            
            if not wizard_state:
                return {
                    "success": False,
                    "error": "Wizard session not found"
                }
            
            # Update wizard state based on step data
            current_step = wizard_state.get("current_step", 1)
            sop_data = wizard_state.get("sop_data", {})
            
            # Process step based on current step number
            if current_step == 1:
                # Step 1: SOP type selection
                sop_type = step_data.get("sop_type", "standard")
                sop_data["template_type"] = sop_type
                wizard_state["next_question"] = "Please provide a title for your SOP"
            elif current_step == 2:
                # Step 2: SOP title
                sop_data["title"] = step_data.get("title", "")
                wizard_state["next_question"] = "Please describe the purpose of this SOP"
            elif current_step == 3:
                # Step 3: SOP purpose
                sop_data["purpose"] = step_data.get("purpose", "")
                wizard_state["next_question"] = "Please describe the procedures (step by step)"
            elif current_step == 4:
                # Step 4: Procedures
                sop_data["procedures"] = step_data.get("procedures", [])
                if isinstance(sop_data["procedures"], str):
                    # Convert string to list if needed
                    sop_data["procedures"] = [sop_data["procedures"]]
                wizard_state["next_question"] = "Would you like to add any additional sections? (optional)"
            elif current_step == 5:
                # Step 5: Additional sections (optional)
                if step_data.get("additional_sections"):
                    sop_data["additional_sections"] = step_data.get("additional_sections", {})
            
            # Update progress
            wizard_state["current_step"] = min(current_step + 1, wizard_state["total_steps"])
            wizard_state["progress_percentage"] = (wizard_state["current_step"] / wizard_state["total_steps"]) * 100
            wizard_state["sop_data"] = sop_data
            wizard_state["updated_at"] = self.clock.now_iso()
            
            # Update wizard session in State Surface
            await self.state_surface.set_session_state(
                session_id=f"{session_id}:{session_token}",
                tenant_id=tenant_id,
                state=wizard_state
            )
            
            self.logger.info(f"✅ Wizard step processed: {current_step}/{wizard_state['total_steps']}")
            
            return {
                "success": True,
                "current_step": wizard_state["current_step"],
                "total_steps": wizard_state["total_steps"],
                "progress_percentage": wizard_state["progress_percentage"],
                "next_question": wizard_state.get("next_question"),
                "wizard_state": wizard_state
            }
        
        except Exception as e:
            self.logger.error(f"Failed to process wizard step: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def complete_wizard(
        self,
        session_id: str,
        tenant_id: str,
        session_token: str
    ) -> Dict[str, Any]:
        """
        Complete wizard and generate SOP.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
            session_token: Wizard session token
        
        Returns:
            Dict with sop_reference and metadata
        """
        try:
            self.logger.info(f"Completing wizard session: {session_token}")
            
            # Get wizard session from State Surface
            wizard_state = await self.state_surface.get_session_state(
                session_id=f"{session_id}:{session_token}",
                tenant_id=tenant_id
            )
            
            if not wizard_state:
                return {
                    "success": False,
                    "error": "Wizard session not found"
                }
            
            # Get SOP data from wizard state
            sop_data = wizard_state.get("sop_data", {})
            template_type = sop_data.get("template_type", "standard")
            
            # Generate SOP structure
            sop_structure = await self._generate_sop_structure(sop_data, template_type)
            
            # Validate SOP
            validation_result = await self.validate_sop(sop_structure)
            
            if not validation_result.get("valid"):
                return {
                    "success": False,
                    "error": "SOP validation failed",
                    "validation_errors": validation_result.get("errors", [])
                }
            
            # Generate SOP content
            sop_content = await self._generate_sop_content(sop_structure, template_type)
            
            # Store SOP artifact in GCS
            sop_id = str(uuid.uuid4())
            storage_path = f"{tenant_id}/{session_id}/{sop_id}/sop.json"
            
            success = await self.file_storage.upload_file(
                file_path=storage_path,
                file_data=json.dumps(sop_content, indent=2).encode('utf-8'),
                metadata={
                    "type": "sop",
                    "template_type": template_type,
                    "created_at": self.clock.now_iso(),
                    "tenant_id": tenant_id,
                    "session_id": session_id,
                    "sop_id": sop_id
                }
            )
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to store SOP artifact"
                }
            
            # Store SOP reference + metadata in State Surface
            sop_reference = f"sop:{tenant_id}:{session_id}:{sop_id}"
            await self.state_surface.store_file_reference(
                session_id=session_id,
                tenant_id=tenant_id,
                file_reference=sop_reference,
                storage_location=storage_path,
                filename=f"sop_{sop_id}.json",
                metadata={
                    "type": "sop",
                    "template_type": template_type,
                    "validation_score": validation_result.get("score", 0),
                    "created_at": self.clock.now_iso()
                }
            )
            
            # Mark wizard session as completed
            wizard_state["completed"] = True
            wizard_state["sop_reference"] = sop_reference
            wizard_state["completed_at"] = self.clock.now_iso()
            await self.state_surface.set_session_state(
                session_id=f"{session_id}:{session_token}",
                tenant_id=tenant_id,
                state=wizard_state
            )
            
            self.logger.info(f"✅ Wizard completed, SOP created: {sop_reference}")
            
            return {
                "success": True,
                "sop_reference": sop_reference,
                "sop_metadata": {
                    "sop_id": sop_id,
                    "template_type": template_type,
                    "validation_score": validation_result.get("score", 0),
                    "storage_location": storage_path
                }
            }
        
        except Exception as e:
            self.logger.error(f"Failed to complete wizard: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_sop(
        self,
        description: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create SOP from description.
        
        Args:
            description: Natural language description of the SOP
            options: Optional creation options (template_type, etc.)
        
        Returns:
            Dict with sop_structure (for agent to use)
        """
        try:
            self.logger.info(f"Creating SOP from description: {description[:50]}...")
            
            template_type = options.get("template_type", "standard") if options else "standard"
            template = self.sop_templates.get(template_type, self.sop_templates["standard"])
            
            # Generate SOP structure from description
            sop_structure = await self._generate_sop_structure_from_description(description, template)
            
            # Generate SOP content
            sop_content = await self._generate_sop_content(sop_structure, template_type)
            
            return {
                "success": True,
                "sop_structure": sop_structure,
                "sop_content": sop_content,
                "template_type": template_type
            }
        
        except Exception as e:
            self.logger.error(f"Failed to create SOP: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_sop(
        self,
        sop_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate SOP structure.
        
        Args:
            sop_data: SOP data to validate
        
        Returns:
            Dict with validation results
        """
        try:
            self.logger.info("Validating SOP structure")
            
            errors = []
            warnings = []
            
            # Get template type
            template_type = sop_data.get("template_type", "standard")
            template = self.sop_templates.get(template_type, self.sop_templates["standard"])
            
            # Check required fields (at top level or in sections)
            required_fields = template.get("required_fields", [])
            for field in required_fields:
                # Check if field exists at top level
                if field in sop_data and sop_data[field]:
                    continue
                # Check if field exists in sections
                sections = sop_data.get("sections", {})
                if field in sections and sections[field]:
                    continue
                # Field not found
                errors.append(f"Missing required field: {field}")
            
            # Check sections (in sections dict or at top level)
            required_sections = template.get("sections", [])
            sections = sop_data.get("sections", {})
            for section in required_sections:
                # Check if section exists in sections dict or at top level
                if section in sections or section in sop_data:
                    continue
                warnings.append(f"Missing recommended section: {section}")
            
            # Calculate score
            max_score = 100
            score = max_score
            score -= len(errors) * 20  # -20 points per error
            score -= len(warnings) * 5  # -5 points per warning
            score = max(0, score)
            
            valid = len(errors) == 0
            
            return {
                "valid": valid,
                "errors": errors,
                "warnings": warnings,
                "score": score
            }
        
        except Exception as e:
            self.logger.error(f"Failed to validate SOP: {e}", exc_info=True)
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "score": 0
            }
    
    async def _generate_sop_structure(
        self,
        sop_data: Dict[str, Any],
        template_type: str
    ) -> Dict[str, Any]:
        """Generate SOP structure from wizard data."""
        template = self.sop_templates.get(template_type, self.sop_templates["standard"])
        
        sop_structure = {
            "template_type": template_type,
            "title": sop_data.get("title", "Untitled SOP"),
            "purpose": sop_data.get("purpose", ""),
            "sections": {}
        }
        
        # Add sections based on template
        for section in template.get("sections", []):
            if section in sop_data:
                sop_structure["sections"][section] = sop_data[section]
            elif section == "procedures":
                sop_structure["sections"]["procedures"] = sop_data.get("procedures", [])
            else:
                sop_structure["sections"][section] = ""
        
        # Add additional sections if provided
        if "additional_sections" in sop_data:
            sop_structure["sections"].update(sop_data["additional_sections"])
        
        return sop_structure
    
    async def _generate_sop_structure_from_description(
        self,
        description: str,
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate SOP structure from natural language description."""
        # Simple structure generation (deterministic)
        # In production, this would be enhanced by agents
        sop_structure = {
            "template_type": "standard",
            "title": description.split(".")[0] if description else "Untitled SOP",
            "purpose": description,
            "sections": {}
        }
        
        # Add sections based on template
        for section in template.get("sections", []):
            sop_structure["sections"][section] = ""
        
        return sop_structure
    
    async def _generate_sop_content(
        self,
        sop_structure: Dict[str, Any],
        template_type: str
    ) -> Dict[str, Any]:
        """Generate SOP content from structure."""
        # Generate formatted SOP content
        sop_content = {
            "sop_id": str(uuid.uuid4()),
            "template_type": template_type,
            "title": sop_structure.get("title", "Untitled SOP"),
            "created_at": self.clock.now_iso(),
            "sections": sop_structure.get("sections", {})
        }
        
        return sop_content
