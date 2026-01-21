#!/usr/bin/env python3
"""
Script to rebuild and restart the Experience service.
This bypasses shell issues by using Python subprocess directly.
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd="/home/founders/demoversion/symphainy_source_code",
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Main execution."""
    print("\n" + "="*60)
    print("🚀 Experience Service Rebuild and Restart")
    print("="*60)
    
    # Step 1: Build Experience service
    if not run_command(
        ["docker-compose", "build", "experience"],
        "Building Experience service"
    ):
        print("\n❌ Build failed. Check errors above.")
        return 1
    
    # Step 2: Stop Experience service
    if not run_command(
        ["docker-compose", "stop", "experience"],
        "Stopping Experience service"
    ):
        print("\n⚠️  Stop command had issues, but continuing...")
    
    # Step 3: Start Experience service
    if not run_command(
        ["docker-compose", "up", "-d", "experience"],
        "Starting Experience service"
    ):
        print("\n❌ Start failed. Check errors above.")
        return 1
    
    # Step 4: Wait for service to be ready
    print("\n⏳ Waiting 10 seconds for service to initialize...")
    time.sleep(10)
    
    # Step 5: Check service status
    if not run_command(
        ["docker-compose", "ps", "experience"],
        "Checking Experience service status"
    ):
        print("\n⚠️  Status check had issues, but service may still be running.")
    
    # Step 6: Check logs for tenant_id processing
    print("\n" + "="*60)
    print("📋 Checking logs for tenant_id processing...")
    print("="*60)
    
    result = subprocess.run(
        ["docker-compose", "logs", "--tail", "50", "experience"],
        cwd="/home/founders/demoversion/symphainy_source_code",
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.stdout:
        logs = result.stdout
        if "tenant_id" in logs.lower() or "EXPERIENCE API" in logs:
            print("✅ Found tenant_id/EXPERIENCE API references in logs")
            # Show relevant lines
            for line in logs.split('\n'):
                if 'tenant_id' in line.lower() or 'EXPERIENCE API' in line:
                    print(f"  {line}")
        else:
            print("ℹ️  No tenant_id references found yet (service may still be starting)")
    
    print("\n" + "="*60)
    print("✅ Experience service rebuild and restart complete!")
    print("="*60)
    print("\nNext step: Run the test:")
    print("  timeout 90 python3 tests/integration/capabilities/phase2/file_management/test_register_file.py")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
