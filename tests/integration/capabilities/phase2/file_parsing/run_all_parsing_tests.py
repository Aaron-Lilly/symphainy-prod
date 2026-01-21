#!/usr/bin/env python3
"""
Comprehensive Parsing Test Suite Runner

Runs all parsing capability tests to ensure ALL parsing capabilities actually work.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Any

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import all test classes
from tests.integration.capabilities.phase2.file_parsing.test_csv_parsing import TestCSVParsing
from tests.integration.capabilities.phase2.file_parsing.test_json_parsing import TestJSONParsing
from tests.integration.capabilities.phase2.file_parsing.test_text_parsing import TestTextParsing
from tests.integration.capabilities.phase2.file_parsing.test_xml_parsing import TestXMLParsing
from tests.integration.capabilities.phase2.file_parsing.test_pdf_parsing import TestPDFParsing
from tests.integration.capabilities.phase2.file_parsing.test_excel_parsing import TestExcelParsing
from tests.integration.capabilities.phase2.file_parsing.test_docx_parsing import TestDOCXParsing
from tests.integration.capabilities.phase2.file_parsing.test_binary_ascii_parsing import TestBinaryASCIIParsing
from tests.integration.capabilities.phase2.file_parsing.test_binary_ebcdic_parsing import TestBinaryEBCDICParsing
from tests.integration.capabilities.phase2.file_parsing.test_image_parsing import TestImageParsing
from tests.integration.capabilities.phase2.file_parsing.test_bpmn_parsing import TestBPMNParsing

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'

class ParsingTestSuite:
    def __init__(self):
        self.tests: List[Tuple[str, Any]] = []
        self.results: List[Tuple[str, bool, str]] = []
    
    def add_test(self, name: str, test_class: Any):
        """Add a test to the suite."""
        self.tests.append((name, test_class))
    
    def print_header(self):
        """Print test suite header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}Comprehensive Parsing Test Suite{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}Testing ALL Parsing Capabilities{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")
        print(f"{Colors.BLUE}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    def print_summary(self):
        """Print test suite summary."""
        total = len(self.results)
        passed = sum(1 for _, result, _ in self.results if result)
        failed = total - passed
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}Test Suite Summary{Colors.RESET}")
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
    suite = ParsingTestSuite()
    
    # Add all parsing tests
    suite.add_test("CSV Parsing", TestCSVParsing)
    suite.add_test("JSON Parsing", TestJSONParsing)
    suite.add_test("Text Parsing", TestTextParsing)
    suite.add_test("XML Parsing", TestXMLParsing)
    suite.add_test("PDF Parsing", TestPDFParsing)
    suite.add_test("Excel Parsing", TestExcelParsing)
    suite.add_test("DOCX Parsing", TestDOCXParsing)
    suite.add_test("Binary Parsing (ASCII)", TestBinaryASCIIParsing)
    suite.add_test("Binary Parsing (EBCDIC)", TestBinaryEBCDICParsing)
    suite.add_test("Image Parsing (OCR)", TestImageParsing)
    suite.add_test("BPMN Parsing", TestBPMNParsing)
    
    # Run all tests
    all_passed = await suite.run_all()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
