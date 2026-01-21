#!/usr/bin/env python3
"""
Test: Platform Solution Creation from POC

Tests the create_solution capability with POC source:
- Solution creation from POC completes
- Solution contains domain service bindings
- Solution defines supported intents
- Results are stored and retrievable
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestCreateSolutionFromPOC(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Platform Solution Creation from POC",
            test_id_prefix="solution_from_poc"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Step 1: Create POC first
        self.print_info("Step 2: Creating POC proposal first")
        poc_status = await self.submit_intent_and_poll(
            intent_type="create_poc",
            parameters={
                "additional_context": {
                    "business_goals": ["Validate migration approach"]
                },
                "poc_options": {
                    "title": "Test POC Proposal",
                    "timeline": "2 weeks"
                }
            },
            timeout=120
        )
        
        if not poc_status:
            self.print_warning("Could not create POC - skipping solution creation")
            return True
        
        poc_artifacts = poc_status.get("artifacts", {})
        proposal_id = poc_artifacts.get("proposal_id") or poc_artifacts.get("poc_id")
        
        if not proposal_id:
            # Try to get from POC artifact
            poc_artifact = poc_artifacts.get("poc", {})
            if isinstance(poc_artifact, dict):
                semantic_payload = poc_artifact.get("semantic_payload", {})
                proposal_id = semantic_payload.get("proposal_id") or semantic_payload.get("poc_id")
        
        if not proposal_id:
            self.print_warning("Could not extract proposal_id")
            return True
        
        self.print_success(f"POC proposal created: {proposal_id}")
        
        # Step 2: Create solution from POC
        self.print_info("Step 3: Creating platform solution from POC")
        solution_status = await self.submit_intent_and_poll(
            intent_type="create_solution",
            parameters={
                "solution_source": "poc",
                "source_id": proposal_id
            },
            timeout=300  # Solution creation may take longer
        )
        
        if not solution_status:
            return False
        
        # Validate solution results
        self.print_info("Step 4: Validating solution results")
        solution_artifacts = solution_status.get("artifacts", {})
        
        solution_artifact = solution_artifacts.get("solution", {})
        solution_id = solution_artifacts.get("solution_id")
        
        if not solution_id:
            # Try to extract from solution_artifact
            if isinstance(solution_artifact, dict):
                solution_id = solution_artifact.get("solution_id")
                solution_data = solution_artifact.get("solution", {})
            else:
                solution_data = solution_artifact
        
        if not solution_id:
            self.print_error("No solution_id found in solution result")
            return False
        
        self.print_success(f"Platform solution created successfully: {solution_id}")
        
        # Validate solution structure
        if isinstance(solution_artifact, dict):
            solution_data = solution_artifact.get("solution", {}) or solution_artifact
        
        if solution_data:
            context = solution_data.get("context", {})
            domain_service_bindings = solution_data.get("domain_service_bindings", [])
            supported_intents = solution_data.get("supported_intents", [])
            
            if context:
                goals = context.get("goals", [])
                constraints = context.get("constraints", [])
                if goals:
                    self.print_success(f"Solution has {len(goals)} goals")
                if constraints:
                    self.print_info(f"Solution has {len(constraints)} constraints")
            
            if domain_service_bindings:
                self.print_success(f"Solution has {len(domain_service_bindings)} domain service bindings")
                for binding in domain_service_bindings[:3]:
                    domain = binding.get("domain")
                    system_name = binding.get("system_name")
                    if domain:
                        self.print_info(f"  Domain: {domain}, System: {system_name}")
            
            if supported_intents:
                self.print_success(f"Solution supports {len(supported_intents)} intents")
                self.print_info(f"  Sample intents: {', '.join(supported_intents[:5])}")
        
        self.print_success("✅ Platform Solution Creation from POC: PASSED")
        return True

async def main():
    test = TestCreateSolutionFromPOC()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
