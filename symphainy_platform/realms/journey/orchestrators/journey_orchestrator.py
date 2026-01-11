"""
Journey Orchestrator

Composes saga steps for Journey operations.
Handles Runtime intents and routes to appropriate services and agents.

WHAT (Journey Realm): I orchestrate Journey operations
HOW (Orchestrator): I compose saga steps, call services, attach agents
"""

import logging
from typing import Dict, Any, Optional

from utilities import get_logger, get_clock

logger = get_logger(__name__)


class JourneyOrchestrator:
    """
    Journey Orchestrator.
    
    Composes saga steps for Journey operations:
    - SOP creation from workflow
    - Workflow creation from SOP
    - SOP wizard management
    - Coexistence analysis
    - Blueprint generation
    - Platform journey creation
    """
    
    def __init__(
        self,
        sop_builder_service: Optional[Any] = None,
        workflow_conversion_service: Optional[Any] = None,
        coexistence_analysis_service: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        file_storage_abstraction: Optional[Any] = None,
        agent_foundation: Optional[Any] = None
    ):
        """
        Initialize Journey Orchestrator.
        
        Args:
            sop_builder_service: SOP Builder Service instance
            workflow_conversion_service: Workflow Conversion Service instance
            coexistence_analysis_service: Coexistence Analysis Service instance
            state_surface: State Surface instance
            file_storage_abstraction: File Storage Abstraction instance
            agent_foundation: Agent Foundation Service instance
        """
        self.sop_builder_service = sop_builder_service
        self.workflow_conversion_service = workflow_conversion_service
        self.coexistence_analysis_service = coexistence_analysis_service
        self.state_surface = state_surface
        self.file_storage = file_storage_abstraction
        self.agent_foundation = agent_foundation
        self.logger = logger
        self.clock = get_clock()
        
        self.logger.info("✅ Journey Orchestrator initialized")
    
    async def create_sop_from_workflow(
        self,
        workflow_reference: str,
        session_id: str,
        tenant_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create SOP from workflow.
        
        Saga: Convert workflow → SOP
        1. Get workflow from State Surface (reference) → retrieve from storage
        2. Call WorkflowConversionService.convert_workflow_to_sop()
        3. Store SOP artifact in GCS
        4. Store SOP reference + metadata in State Surface
        5. Return SOP reference
        
        Args:
            workflow_reference: State Surface reference to workflow
            session_id: Session identifier
            tenant_id: Tenant identifier
            options: Optional conversion options
        
        Returns:
            Dict with sop_reference and metadata
        """
        try:
            self.logger.info(f"Creating SOP from workflow: {workflow_reference}")
            
            if not self.workflow_conversion_service:
                return {
                    "success": False,
                    "error": "Workflow Conversion Service not available"
                }
            
            # Step 1: Convert workflow to SOP structure
            conversion_result = await self.workflow_conversion_service.convert_workflow_to_sop(
                workflow_file_reference=workflow_reference,
                options=options
            )
            
            if not conversion_result.get("success"):
                return conversion_result
            
            sop_structure = conversion_result.get("sop_structure")
            if not sop_structure:
                return {
                    "success": False,
                    "error": "Failed to generate SOP structure"
                }
            
            # Step 2: Store SOP artifact in GCS
            import json
            import uuid
            sop_id = str(uuid.uuid4())
            storage_path = f"{tenant_id}/{session_id}/{sop_id}/sop.json"
            
            sop_content = {
                "sop_id": sop_id,
                "title": sop_structure.get("title", "Untitled SOP"),
                "template_type": sop_structure.get("template_type", "standard"),
                "sections": sop_structure.get("sections", {}),
                "metadata": sop_structure.get("metadata", {}),
                "created_at": self.clock.now_iso(),
                "source_workflow": workflow_reference
            }
            
            success = await self.file_storage.upload_file(
                file_path=storage_path,
                file_data=json.dumps(sop_content, indent=2).encode('utf-8'),
                metadata={
                    "type": "sop",
                    "template_type": sop_structure.get("template_type", "standard"),
                    "created_at": self.clock.now_iso(),
                    "tenant_id": tenant_id,
                    "session_id": session_id,
                    "sop_id": sop_id,
                    "source_workflow": workflow_reference
                }
            )
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to store SOP artifact"
                }
            
            # Step 3: Store SOP reference + metadata in State Surface
            sop_reference = f"sop:{tenant_id}:{session_id}:{sop_id}"
            await self.state_surface.store_file_reference(
                session_id=session_id,
                tenant_id=tenant_id,
                file_reference=sop_reference,
                storage_location=storage_path,
                filename=f"sop_{sop_id}.json",
                metadata={
                    "type": "sop",
                    "template_type": sop_structure.get("template_type", "standard"),
                    "source_workflow": workflow_reference,
                    "created_at": self.clock.now_iso()
                }
            )
            
            self.logger.info(f"✅ SOP created from workflow: {sop_reference}")
            
            return {
                "success": True,
                "sop_reference": sop_reference,
                "sop_metadata": {
                    "sop_id": sop_id,
                    "template_type": sop_structure.get("template_type", "standard"),
                    "storage_location": storage_path,
                    "source_workflow": workflow_reference
                }
            }
        
        except Exception as e:
            self.logger.error(f"Failed to create SOP from workflow: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_workflow_from_sop(
        self,
        sop_file_reference: str,
        session_id: str,
        tenant_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create workflow from SOP.
        
        Saga: Convert SOP → Workflow
        1. Get SOP from State Surface (reference) → retrieve from GCS
        2. Call WorkflowConversionService.convert_sop_to_workflow()
        3. Store workflow artifact in GCS (ArangoDB integration deferred)
        4. Store workflow reference + metadata in State Surface
        5. Return workflow reference
        
        Args:
            sop_file_reference: State Surface reference to SOP
            session_id: Session identifier
            tenant_id: Tenant identifier
            options: Optional conversion options
        
        Returns:
            Dict with workflow_reference and metadata
        """
        try:
            self.logger.info(f"Creating workflow from SOP: {sop_file_reference}")
            
            if not self.workflow_conversion_service:
                return {
                    "success": False,
                    "error": "Workflow Conversion Service not available"
                }
            
            # Step 1: Convert SOP to workflow structure
            conversion_result = await self.workflow_conversion_service.convert_sop_to_workflow(
                sop_file_reference=sop_file_reference,
                options=options
            )
            
            if not conversion_result.get("success"):
                return conversion_result
            
            workflow_structure = conversion_result.get("workflow_structure")
            if not workflow_structure:
                return {
                    "success": False,
                    "error": "Failed to generate workflow structure"
                }
            
            # Step 2: Store workflow artifact in GCS (ArangoDB integration deferred)
            import json
            import uuid
            workflow_id = str(uuid.uuid4())
            storage_path = f"{tenant_id}/{session_id}/{workflow_id}/workflow.json"
            
            workflow_content = {
                "workflow_id": workflow_id,
                "workflow_name": workflow_structure.get("workflow_name", "Untitled Workflow"),
                "workflow_type": workflow_structure.get("workflow_type", "sequential"),
                "description": workflow_structure.get("description", ""),
                "nodes": workflow_structure.get("nodes", []),
                "edges": workflow_structure.get("edges", []),
                "metadata": workflow_structure.get("metadata", {}),
                "created_at": self.clock.now_iso(),
                "source_sop": sop_file_reference
            }
            
            success = await self.file_storage.upload_file(
                file_path=storage_path,
                file_data=json.dumps(workflow_content, indent=2).encode('utf-8'),
                metadata={
                    "type": "workflow",
                    "workflow_type": workflow_structure.get("workflow_type", "sequential"),
                    "created_at": self.clock.now_iso(),
                    "tenant_id": tenant_id,
                    "session_id": session_id,
                    "workflow_id": workflow_id,
                    "source_sop": sop_file_reference
                }
            )
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to store workflow artifact"
                }
            
            # Step 3: Store workflow reference + metadata in State Surface
            workflow_reference = f"workflow:{tenant_id}:{session_id}:{workflow_id}"
            await self.state_surface.store_file_reference(
                session_id=session_id,
                tenant_id=tenant_id,
                file_reference=workflow_reference,
                storage_location=storage_path,
                filename=f"workflow_{workflow_id}.json",
                metadata={
                    "type": "workflow",
                    "workflow_type": workflow_structure.get("workflow_type", "sequential"),
                    "source_sop": sop_file_reference,
                    "created_at": self.clock.now_iso()
                }
            )
            
            self.logger.info(f"✅ Workflow created from SOP: {workflow_reference}")
            
            return {
                "success": True,
                "workflow_reference": workflow_reference,
                "workflow_metadata": {
                    "workflow_id": workflow_id,
                    "workflow_type": workflow_structure.get("workflow_type", "sequential"),
                    "storage_location": storage_path,
                    "source_sop": sop_file_reference
                }
            }
        
        except Exception as e:
            self.logger.error(f"Failed to create workflow from SOP: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def start_sop_wizard(
        self,
        session_id: str,
        tenant_id: str,
        initial_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start SOP wizard session.
        
        Saga: Start SOP wizard session
        1. Call SOPBuilderService.start_wizard_session()
        2. Service stores wizard session state in State Surface
        3. Return session token
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
            initial_description: Optional initial process description
        
        Returns:
            Dict with wizard_session_token and wizard_state
        """
        try:
            self.logger.info(f"Starting SOP wizard session for tenant: {tenant_id}, session: {session_id}")
            
            if not self.sop_builder_service:
                return {
                    "success": False,
                    "error": "SOP Builder Service not available"
                }
            
            # Call service (service handles State Surface storage)
            result = await self.sop_builder_service.start_wizard_session(
                session_id=session_id,
                tenant_id=tenant_id,
                initial_description=initial_description
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to start SOP wizard: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_sop_wizard_step(
        self,
        session_id: str,
        tenant_id: str,
        session_token: str,
        step_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process wizard step.
        
        Saga: Process wizard step
        1. Get wizard session from State Surface (via service)
        2. Attach SOPBuilderWizardAgent for reasoning (if needed - Phase 6)
        3. Call SOPBuilderService.process_wizard_step()
        4. Service updates session state in State Surface
        5. Return step result
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
            session_token: Wizard session token
            step_data: Step data from user
        
        Returns:
            Dict with step result
        """
        try:
            self.logger.info(f"Processing wizard step for session: {session_token}")
            
            if not self.sop_builder_service:
                return {
                    "success": False,
                    "error": "SOP Builder Service not available"
                }
            
            # Note: Agent reasoning will be added in Phase 6
            # For now, service processes step directly
            
            # Call service (service handles State Surface updates)
            result = await self.sop_builder_service.process_wizard_step(
                session_id=session_id,
                tenant_id=tenant_id,
                session_token=session_token,
                step_data=step_data
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to process wizard step: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def complete_sop_wizard(
        self,
        session_id: str,
        tenant_id: str,
        session_token: str
    ) -> Dict[str, Any]:
        """
        Complete wizard and generate SOP.
        
        Saga: Complete wizard and generate SOP
        1. Get wizard session from State Surface (via service)
        2. Attach SOPBuilderWizardAgent for final reasoning (Phase 6)
        3. Call SOPBuilderService.complete_wizard()
        4. Service stores SOP artifact in GCS
        5. Service stores SOP reference + metadata in State Surface
        6. Return SOP reference
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
            session_token: Wizard session token
        
        Returns:
            Dict with sop_reference and metadata
        """
        try:
            self.logger.info(f"Completing wizard session: {session_token}")
            
            if not self.sop_builder_service:
                return {
                    "success": False,
                    "error": "SOP Builder Service not available"
                }
            
            # Note: Agent reasoning will be added in Phase 6
            # For now, service completes wizard directly
            
            # Call service (service handles artifact storage and State Surface updates)
            result = await self.sop_builder_service.complete_wizard(
                session_id=session_id,
                tenant_id=tenant_id,
                session_token=session_token
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to complete wizard: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_coexistence(
        self,
        session_id: str,
        tenant_id: str,
        workflow_reference: Optional[str] = None,
        sop_reference: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze coexistence opportunities.
        
        Saga: Analyze coexistence opportunities
        1. Get workflow/SOP from State Surface (references) → retrieve from storage
        2. Attach CoexistenceAnalyzerAgent for reasoning (Phase 6)
        3. Call CoexistenceAnalysisService.analyze_coexistence()
        4. Store analysis in State Surface (facts + references)
        5. Return analysis reference
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
            workflow_reference: Optional State Surface reference to workflow
            sop_reference: Optional State Surface reference to SOP
            options: Optional analysis options
        
        Returns:
            Dict with analysis_reference and metadata
        """
        try:
            self.logger.info(f"Analyzing coexistence opportunities")
            
            if not self.coexistence_analysis_service:
                return {
                    "success": False,
                    "error": "Coexistence Analysis Service not available"
                }
            
            # Step 1: Get workflow/SOP content from State Surface
            current_state = {}
            target_state = None
            
            if workflow_reference:
                # Get workflow from State Surface
                workflow_metadata = await self.state_surface.get_file_metadata(workflow_reference)
                if workflow_metadata:
                    storage_location = workflow_metadata.get("storage_location")
                    if storage_location:
                        workflow_data = await self.file_storage.download_file(storage_location)
                        if workflow_data:
                            import json
                            current_state = json.loads(workflow_data.decode('utf-8'))
            
            if sop_reference:
                # Get SOP from State Surface
                sop_metadata = await self.state_surface.get_file_metadata(sop_reference)
                if sop_metadata:
                    storage_location = sop_metadata.get("storage_location")
                    if storage_location:
                        sop_data = await self.file_storage.download_file(storage_location)
                        if sop_data:
                            import json
                            # If we already have workflow, use SOP as target state
                            if current_state:
                                target_state = json.loads(sop_data.decode('utf-8'))
                            else:
                                current_state = json.loads(sop_data.decode('utf-8'))
            
            if not current_state:
                return {
                    "success": False,
                    "error": "No workflow or SOP reference provided or not found"
                }
            
            # Step 2: Call service for analysis
            # Note: Agent reasoning will be added in Phase 6
            analysis_result = await self.coexistence_analysis_service.analyze_coexistence(
                current_state=current_state,
                target_state=target_state
            )
            
            if not analysis_result.get("success"):
                return analysis_result
            
            analysis_data = analysis_result.get("analysis_result")
            if not analysis_data:
                return {
                    "success": False,
                    "error": "Failed to generate analysis result"
                }
            
            # Step 3: Store analysis in State Surface (facts + references)
            import uuid
            analysis_id = analysis_data.get("analysis_id", str(uuid.uuid4()))
            analysis_reference = f"analysis:{tenant_id}:{session_id}:{analysis_id}"
            
            # Store analysis in session state
            analysis_state = {
                **analysis_data,
                "type": "coexistence_analysis",
                "workflow_reference": workflow_reference,
                "sop_reference": sop_reference,
                "created_at": self.clock.now_iso()
            }
            await self.state_surface.set_session_state(
                session_id=f"{session_id}:{analysis_id}",
                tenant_id=tenant_id,
                state=analysis_state
            )
            
            self.logger.info(f"✅ Coexistence analysis complete: {analysis_reference}")
            
            return {
                "success": True,
                "analysis_reference": analysis_reference,
                "analysis_metadata": {
                    "analysis_id": analysis_id,
                    "opportunities_count": len(analysis_data.get("opportunities", [])),
                    "recommended_patterns": analysis_data.get("recommended_patterns", [])
                }
            }
        
        except Exception as e:
            self.logger.error(f"Failed to analyze coexistence: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_coexistence_blueprint(
        self,
        analysis_reference: str,
        session_id: str,
        tenant_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate coexistence blueprint.
        
        Saga: Generate coexistence blueprint
        1. Get analysis from State Surface
        2. Attach CoexistenceAnalyzerAgent for reasoning (Phase 6)
        3. Call CoexistenceAnalysisService.generate_blueprint()
        4. Store blueprint artifact in GCS
        5. Store blueprint reference + metadata in State Surface
        6. Return blueprint reference
        
        Args:
            analysis_reference: State Surface reference to analysis
            session_id: Session identifier
            tenant_id: Tenant identifier
            options: Optional blueprint generation options
        
        Returns:
            Dict with blueprint_reference and metadata
        """
        try:
            self.logger.info(f"Generating coexistence blueprint from analysis: {analysis_reference}")
            
            if not self.coexistence_analysis_service:
                return {
                    "success": False,
                    "error": "Coexistence Analysis Service not available"
                }
            
            # Step 1: Get analysis from State Surface
            # Extract analysis_id from reference
            analysis_id = analysis_reference.split(":")[-1] if ":" in analysis_reference else analysis_reference
            analysis_data = await self.state_surface.get_session_state(
                session_id=f"{session_id}:{analysis_id}",
                tenant_id=tenant_id
            )
            if not analysis_data:
                return {
                    "success": False,
                    "error": "Analysis reference not found in State Surface"
                }
            
            # Step 2: Call service to generate blueprint
            # Note: Agent reasoning will be added in Phase 6
            blueprint_result = await self.coexistence_analysis_service.generate_blueprint(
                analysis_result=analysis_data,
                options=options
            )
            
            if not blueprint_result.get("success"):
                return blueprint_result
            
            blueprint_structure = blueprint_result.get("blueprint_structure")
            if not blueprint_structure:
                return {
                    "success": False,
                    "error": "Failed to generate blueprint structure"
                }
            
            # Step 3: Store blueprint artifact in GCS
            import json
            import uuid
            blueprint_id = blueprint_structure.get("blueprint_id", str(uuid.uuid4()))
            storage_path = f"{tenant_id}/{session_id}/{blueprint_id}/blueprint.json"
            
            blueprint_content = {
                "blueprint_id": blueprint_id,
                "blueprint_name": blueprint_structure.get("blueprint_name", "Coexistence Blueprint"),
                "analysis_id": blueprint_structure.get("analysis_id"),
                "recommended_patterns": blueprint_structure.get("recommended_patterns", []),
                "implementation_plan": blueprint_structure.get("implementation_plan", {}),
                "optimization_metrics": blueprint_structure.get("optimization_metrics", {}),
                "metadata": blueprint_structure.get("metadata", {}),
                "created_at": self.clock.now_iso(),
                "source_analysis": analysis_reference
            }
            
            success = await self.file_storage.upload_file(
                file_path=storage_path,
                file_data=json.dumps(blueprint_content, indent=2).encode('utf-8'),
                metadata={
                    "type": "coexistence_blueprint",
                    "created_at": self.clock.now_iso(),
                    "tenant_id": tenant_id,
                    "session_id": session_id,
                    "blueprint_id": blueprint_id,
                    "source_analysis": analysis_reference
                }
            )
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to store blueprint artifact"
                }
            
            # Step 4: Store blueprint reference + metadata in State Surface
            blueprint_reference = f"blueprint:{tenant_id}:{session_id}:{blueprint_id}"
            await self.state_surface.store_file_reference(
                session_id=session_id,
                tenant_id=tenant_id,
                file_reference=blueprint_reference,
                storage_location=storage_path,
                filename=f"blueprint_{blueprint_id}.json",
                metadata={
                    "type": "coexistence_blueprint",
                    "source_analysis": analysis_reference,
                    "created_at": self.clock.now_iso()
                }
            )
            
            self.logger.info(f"✅ Coexistence blueprint generated: {blueprint_reference}")
            
            return {
                "success": True,
                "blueprint_reference": blueprint_reference,
                "blueprint_metadata": {
                    "blueprint_id": blueprint_id,
                    "storage_location": storage_path,
                    "source_analysis": analysis_reference,
                    "recommended_patterns": blueprint_structure.get("recommended_patterns", [])
                }
            }
        
        except Exception as e:
            self.logger.error(f"Failed to generate blueprint: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_platform_journey(
        self,
        blueprint_reference: str,
        session_id: str,
        tenant_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Turn blueprint into platform journey.
        
        Saga: Turn blueprint into platform journey
        1. Get blueprint from State Surface (reference) → retrieve from GCS
        2. Attach JourneyGeneratorAgent for reasoning (Phase 6 - if needed)
        3. Generate journey definition
        4. Store journey in GCS (ArangoDB integration deferred)
        5. Store journey reference + metadata in State Surface
        6. Return journey reference
        
        Args:
            blueprint_reference: State Surface reference to blueprint
            session_id: Session identifier
            tenant_id: Tenant identifier
            options: Optional journey creation options
        
        Returns:
            Dict with journey_reference and metadata
        """
        try:
            self.logger.info(f"Creating platform journey from blueprint: {blueprint_reference}")
            
            # Step 1: Get blueprint from State Surface
            blueprint_metadata = await self.state_surface.get_file_metadata(blueprint_reference)
            if not blueprint_metadata:
                return {
                    "success": False,
                    "error": "Blueprint reference not found in State Surface"
                }
            
            storage_location = blueprint_metadata.get("storage_location")
            if not storage_location:
                return {
                    "success": False,
                    "error": "Blueprint storage location not found"
                }
            
            # Retrieve blueprint artifact from GCS
            blueprint_data = await self.file_storage.download_file(storage_location)
            if not blueprint_data:
                return {
                    "success": False,
                    "error": "Failed to retrieve blueprint artifact"
                }
            
            import json
            blueprint_content = json.loads(blueprint_data.decode('utf-8'))
            
            # Step 2: Generate journey definition from blueprint
            # Note: Agent reasoning will be added in Phase 6
            # For now, generate deterministic journey structure
            import uuid
            journey_id = str(uuid.uuid4())
            
            journey_definition = {
                "journey_id": journey_id,
                "journey_name": f"Platform Journey - {blueprint_content.get('blueprint_name', 'Untitled')}",
                "description": f"Platform journey generated from coexistence blueprint",
                "blueprint_reference": blueprint_reference,
                "implementation_plan": blueprint_content.get("implementation_plan", {}),
                "recommended_patterns": blueprint_content.get("recommended_patterns", []),
                "optimization_metrics": blueprint_content.get("optimization_metrics", {}),
                "metadata": {
                    "source_blueprint": blueprint_reference,
                    "created_at": self.clock.now_iso(),
                    "tenant_id": tenant_id,
                    "session_id": session_id
                }
            }
            
            # Step 3: Store journey in GCS (ArangoDB integration deferred)
            journey_storage_path = f"{tenant_id}/{session_id}/{journey_id}/journey.json"
            
            success = await self.file_storage.upload_file(
                file_path=journey_storage_path,
                file_data=json.dumps(journey_definition, indent=2).encode('utf-8'),
                metadata={
                    "type": "platform_journey",
                    "created_at": self.clock.now_iso(),
                    "tenant_id": tenant_id,
                    "session_id": session_id,
                    "journey_id": journey_id,
                    "source_blueprint": blueprint_reference
                }
            )
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to store journey artifact"
                }
            
            # Step 4: Store journey reference + metadata in State Surface
            journey_reference = f"journey:{tenant_id}:{session_id}:{journey_id}"
            await self.state_surface.store_file_reference(
                session_id=session_id,
                tenant_id=tenant_id,
                file_reference=journey_reference,
                storage_location=journey_storage_path,
                filename=f"journey_{journey_id}.json",
                metadata={
                    "type": "platform_journey",
                    "source_blueprint": blueprint_reference,
                    "created_at": self.clock.now_iso()
                }
            )
            
            self.logger.info(f"✅ Platform journey created: {journey_reference}")
            
            return {
                "success": True,
                "journey_reference": journey_reference,
                "journey_metadata": {
                    "journey_id": journey_id,
                    "storage_location": journey_storage_path,
                    "source_blueprint": blueprint_reference,
                    "journey_name": journey_definition.get("journey_name")
                }
            }
        
        except Exception as e:
            self.logger.error(f"Failed to create platform journey: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
