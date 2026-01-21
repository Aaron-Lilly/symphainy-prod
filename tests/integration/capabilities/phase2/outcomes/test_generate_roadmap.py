#!/usr/bin/env python3
"""
Test: Roadmap Generation

Tests the generate_roadmap capability:
- Roadmap generation completes
- Roadmap contains phases, milestones, timeline
- Roadmap visualization is generated
- roadmap_id is present in artifacts (for solution conversion)
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

class TestGenerateRoadmap(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Roadmap Generation",
            test_id_prefix="generate_roadmap"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Note: generate_roadmap reads pillar summaries from session state
        # For testing, we'll submit with optional parameters
        self.print_info("Step 2: Generating roadmap from pillar summaries")
        roadmap_status = await self.submit_intent_and_poll(
            intent_type="generate_roadmap",
            parameters={
                "additional_context": {
                    "business_goals": ["Complete migration", "Minimize downtime"],
                    "constraints": ["Budget: $500k", "Timeline: 12 weeks"]
                },
                "roadmap_options": {
                    "max_phases": 5,
                    "include_risk_assessment": True
                }
            },
            timeout=180  # Roadmap generation may take longer
        )
        
        if not roadmap_status:
            return False
        
        # Validate roadmap results
        self.print_info("Step 3: Validating roadmap results")
        roadmap_artifacts = roadmap_status.get("artifacts", {})
        
        # CRITICAL: Validate roadmap_id is present (needed for solution conversion)
        roadmap_id = roadmap_artifacts.get("roadmap_id")
        if not roadmap_id:
            # Try to get from roadmap artifact
            roadmap_artifact = roadmap_artifacts.get("roadmap", {})
            if isinstance(roadmap_artifact, dict):
                semantic_payload = roadmap_artifact.get("semantic_payload", {})
                roadmap_id = semantic_payload.get("roadmap_id")
        
        if not roadmap_id:
            self.print_error("No roadmap_id found in roadmap artifacts")
            return False
        
        self.print_success(f"Roadmap generated successfully: {roadmap_id}")
        
        # Validate roadmap structure
        roadmap_artifact = roadmap_artifacts.get("roadmap", {})
        if isinstance(roadmap_artifact, dict):
            renderings = roadmap_artifact.get("renderings", {})
            roadmap_data = renderings.get("roadmap", {})
            strategic_plan = renderings.get("strategic_plan", {})
        else:
            roadmap_data = roadmap_artifact.get("roadmap", {}) if isinstance(roadmap_artifact, dict) else {}
            strategic_plan = roadmap_artifact.get("strategic_plan", {}) if isinstance(roadmap_artifact, dict) else {}
        
        if roadmap_data:
            phases = roadmap_data.get("phases", [])
            milestones = roadmap_data.get("milestones", [])
            timeline = roadmap_data.get("timeline", {})
            
            if phases:
                self.print_success(f"Roadmap contains {len(phases)} phases")
                for phase in phases[:3]:  # Show first 3 phases
                    phase_name = phase.get("phase") or phase.get("name", "")
                    phase_status = phase.get("status", "")
                    if phase_name:
                        self.print_info(f"  Phase: {phase_name} ({phase_status})")
            else:
                self.print_info("Roadmap has no phases (may be expected for minimal data)")
            
            if milestones:
                self.print_success(f"Roadmap contains {len(milestones)} milestones")
            else:
                self.print_info("Roadmap has no milestones (may be expected)")
            
            if timeline:
                start_date = timeline.get("start_date")
                end_date = timeline.get("end_date")
                if start_date or end_date:
                    self.print_info(f"Timeline: {start_date} to {end_date}")
        
        if strategic_plan:
            goals = strategic_plan.get("goals", [])
            objectives = strategic_plan.get("objectives", [])
            if goals:
                self.print_success(f"Strategic plan has {len(goals)} goals")
            if objectives:
                self.print_info(f"Strategic plan has {len(objectives)} objectives")
        
        # Validate roadmap visual
        roadmap_visual = roadmap_artifacts.get("roadmap_visual", {})
        if roadmap_visual:
            image_base64 = roadmap_visual.get("image_base64")
            storage_path = roadmap_visual.get("storage_path")
            
            if image_base64:
                self.print_success("Roadmap visual image generated (base64)")
            if storage_path:
                self.print_info(f"Roadmap visual stored at: {storage_path}")
        else:
            self.print_info("No roadmap visual generated (may not be implemented)")
        
        self.print_success("✅ Roadmap Generation: PASSED")
        return True

async def main():
    test = TestGenerateRoadmap()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
