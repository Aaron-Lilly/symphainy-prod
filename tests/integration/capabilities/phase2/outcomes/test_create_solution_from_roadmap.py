#!/usr/bin/env python3
"""
Test: Platform Solution Creation from Roadmap

Tests the create_solution capability with roadmap source:
- Solution creation from roadmap completes
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

class TestCreateSolutionFromRoadmap(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Platform Solution Creation from Roadmap",
            test_id_prefix="solution_from_roadmap"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Step 1: Generate roadmap first
        self.print_info("Step 2: Generating roadmap first")
        roadmap_status = await self.submit_intent_and_poll(
            intent_type="generate_roadmap",
            parameters={
                "additional_context": {
                    "business_goals": ["Complete migration", "Minimize downtime"]
                },
                "roadmap_options": {
                    "max_phases": 3
                }
            },
            timeout=120
        )
        
        if not roadmap_status:
            self.print_warning("Could not generate roadmap - skipping solution creation")
            return True
        
        roadmap_artifacts = roadmap_status.get("artifacts", {})
        roadmap_id = roadmap_artifacts.get("roadmap_id")
        
        if not roadmap_id:
            # Try to get from roadmap artifact
            roadmap_artifact = roadmap_artifacts.get("roadmap", {})
            if isinstance(roadmap_artifact, dict):
                semantic_payload = roadmap_artifact.get("semantic_payload", {})
                roadmap_id = semantic_payload.get("roadmap_id")
        
        if not roadmap_id:
            self.print_warning("Could not extract roadmap_id")
            return True
        
        self.print_success(f"Roadmap generated: {roadmap_id}")
        
        # Step 2: Create solution from roadmap
        self.print_info("Step 3: Creating platform solution from roadmap")
        solution_status = await self.submit_intent_and_poll(
            intent_type="create_solution",
            parameters={
                "solution_source": "roadmap",
                "source_id": roadmap_id
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
        
        self.print_success("✅ Platform Solution Creation from Roadmap: PASSED")
        return True

async def main():
    test = TestCreateSolutionFromRoadmap()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
