#!/usr/bin/env python3
"""
Script to run the test_register_file.py test.
This bypasses shell issues by using Python subprocess directly.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the test."""
    test_path = Path("/home/founders/demoversion/symphainy_source_code/tests/integration/capabilities/phase2/file_management/test_register_file.py")
    
    if not test_path.exists():
        print(f"❌ Test file not found: {test_path}")
        return 1
    
    print("\n" + "="*60)
    print("🧪 Running test_register_file.py")
    print("="*60)
    print(f"Test: {test_path}")
    print()
    
    try:
        result = subprocess.run(
            ["timeout", "90", "python3", str(test_path)],
            cwd="/home/founders/demoversion/symphainy_source_code",
            timeout=120  # 2 minute timeout for the timeout command itself
        )
        
        if result.returncode == 0:
            print("\n✅ Test PASSED")
            return 0
        else:
            print(f"\n❌ Test FAILED (exit code: {result.returncode})")
            return result.returncode
            
    except subprocess.TimeoutExpired:
        print("\n⏱️  Test TIMEOUT (exceeded 90 seconds)")
        return 124  # Standard timeout exit code
    except Exception as e:
        print(f"\n❌ Test execution error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
