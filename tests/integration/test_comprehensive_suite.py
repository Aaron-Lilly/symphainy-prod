#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner

Runs all test suites in order of priority:
1. Security & Authentication (Critical)
2. WebSocket Robustness (High)
3. Error Handling & Edge Cases (Medium)
4. Performance & Load (Medium)
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import subprocess
from typing import Dict, Any


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(text)
    print(f"{'='*60}{Colors.RESET}\n")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def run_test_suite(test_file: str, suite_name: str) -> bool:
    """Run a test suite and return success status."""
    print_header(f"Running: {suite_name}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=project_root,
            capture_output=False,
            timeout=600  # 10 minute timeout per suite (for rate limit waits)
        )
        
        if result.returncode == 0:
            print_success(f"{suite_name} completed successfully")
            return True
        else:
            print_error(f"{suite_name} had failures (exit code: {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print_error(f"{suite_name} timed out after 10 minutes")
        return False
    except Exception as e:
        print_error(f"{suite_name} failed to run: {e}")
        return False


def main():
    """Run all test suites."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("Comprehensive Platform Test Suite")
    print("Pressure Testing Before Executive Demo")
    print(f"{'='*60}{Colors.RESET}\n")
    
    test_suites = [
        # Priority 1: Critical Security
        (
            "tests/integration/test_auth_security_comprehensive.py",
            "Priority 1: Authentication & Security (Critical)"
        ),
        
        # Priority 2: High Priority WebSocket
        (
            "tests/integration/test_websocket_robustness.py",
            "Priority 2: WebSocket Robustness (High)"
        ),
        
        # Priority 3: Error Handling
        (
            "tests/integration/test_error_handling_edge_cases.py",
            "Priority 3: Error Handling & Edge Cases (Medium)"
        ),
        
        # Priority 4: Performance
        (
            "tests/integration/test_performance_load.py",
            "Priority 4: Performance & Load (Medium)"
        ),
    ]
    
    results = {}
    
    for test_file, suite_name in test_suites:
        test_path = project_root / test_file
        if not test_path.exists():
            print_error(f"Test file not found: {test_file}")
            results[suite_name] = False
            continue
        
        results[suite_name] = run_test_suite(str(test_path), suite_name)
    
    # Final Summary
    print_header("Final Test Summary")
    
    for suite_name, passed in results.items():
        if passed:
            print_success(f"{suite_name}: PASSED")
        else:
            print_error(f"{suite_name}: FAILED")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} test suites passed{Colors.RESET}\n")
    
    if passed == total:
        print_success("🎉 All test suites passed! Platform is ready for executive demo.")
        return 0
    else:
        print_error(f"⚠️  {total - passed} test suite(s) had failures. Review before demo.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
