#!/usr/bin/env python3
"""
Journey Realm Capability Tests Runner

Runs all Journey Realm capability tests to validate complete functionality.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Any

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import all Journey Realm test classes
from tests.integration.capabilities.phase2.journey_realm.sop_generation.test_generate_sop_from_workflow import TestGenerateSOPFromWorkflow
from tests.integration.capabilities.phase2.journey_realm.sop_generation.test_generate_sop_from_chat import TestGenerateSOPFromChat
from tests.integration.capabilities.phase2.journey_realm.workflow_creation.test_create_workflow_from_sop import TestCreateWorkflowFromSOP
from tests.integration.capabilities.phase2.journey_realm.workflow_creation.test_create_workflow_from_bpmn import TestCreateWorkflowFromBPMN
from tests.integration.capabilities.phase2.journey_realm.test_optimize_process import TestOptimizeProcess
from tests.integration.capabilities.phase2.journey_realm.coexistence.test_analyze_coexistence import TestAnalyzeCoexistence
from tests.integration.capabilities.phase2.journey_realm.coexistence.test_create_blueprint import TestCreateBlueprint
from tests.integration.capabilities.phase2.journey_realm.coexistence.test_create_solution_from_blueprint import TestCreateSolutionFromBlueprint

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'

class JourneyRealmTestSuite:
    def __init__(self):
        self.tests: List[Tuple[str, Any]] = []
        self.results: List[Tuple[str, bool, str]] = []
    
    def add_test(self, name: str, test_class: Any):
        """Add a test to the suite."""
        self.tests.append((name, test_class))
    
    def print_header(self):
        """Print test suite header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}Journey Realm Capability Tests{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}Complete Capability Coverage{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")
        print(f"{Colors.BLUE}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    def print_summary(self):
        """Print test suite summary."""
        total = len(self.results)
        passed = sum(1 for _, result, _ in self.results if result)
        failed = total - passed
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}Journey Realm Test Suite Summary{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")
        
        print(f"{Colors.BLUE}Total Tests: {total}{Colors.RESET}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}\n")
        
        if failed > 0:
            print(f"{Colors.RED}Failed Tests:{Colors.RESET}")
            for name, result, error in self.results:
                if not result:
                    print(f"  {Colors.RED}❌ {name}{Colors.RESET}")
                    if error:
                        print(f"     {Colors.YELLOW}{error}{Colors.RESET}")
        
        print(f"\n{Colors.BLUE}Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
        
        return failed == 0
    
    async def run_all(self) -> bool:
        """Run all tests in the suite."""
        self.print_header()
        
        for name, test_class in self.tests:
            print(f"\n{Colors.BOLD}{Colors.BLUE}{'─'*80}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.BLUE}Running: {name}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.BLUE}{'─'*80}{Colors.RESET}\n")
            
            try:
                test = test_class()
                result = await test.execute()
                error = None
            except Exception as e:
                result = False
                error = str(e)
                import traceback
                print(f"{Colors.RED}Test execution error: {e}{Colors.RESET}")
                traceback.print_exc()
            
            self.results.append((name, result, error))
            
            if result:
                print(f"\n{Colors.GREEN}✅ {name}: PASSED{Colors.RESET}\n")
            else:
                print(f"\n{Colors.RED}❌ {name}: FAILED{Colors.RESET}\n")
        
        return self.print_summary()

async def main():
    suite = JourneyRealmTestSuite()
    
    # Add all Journey Realm tests
    suite.add_test("SOP Generation from Workflow", TestGenerateSOPFromWorkflow)
    suite.add_test("SOP Generation from Chat (LLM Validation)", TestGenerateSOPFromChat)
    suite.add_test("Workflow Creation from SOP", TestCreateWorkflowFromSOP)
    suite.add_test("Workflow Creation from BPMN", TestCreateWorkflowFromBPMN)
    suite.add_test("Process Optimization", TestOptimizeProcess)
    suite.add_test("Coexistence Analysis", TestAnalyzeCoexistence)
    suite.add_test("Coexistence Blueprint Creation", TestCreateBlueprint)
    suite.add_test("Platform Journey Translation", TestCreateSolutionFromBlueprint)
    
    # Run all tests
    all_passed = await suite.run_all()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
