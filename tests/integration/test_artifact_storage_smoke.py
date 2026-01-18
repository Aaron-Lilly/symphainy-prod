"""
Smoke Test for Artifact Storage (Phase 1)

Lightweight test to verify artifact storage foundation is working.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add utilities to path
utilities_path = project_root / "utilities"
if str(utilities_path) not in sys.path:
    sys.path.insert(0, str(utilities_path))

try:
    from utilities import get_logger
except ImportError:
    # Fallback if utilities not found
    def get_logger(name):
        import logging
        return logging.getLogger(name)

logger = get_logger("ArtifactStorageSmokeTest")


async def test_artifact_storage_foundation():
    """Test that artifact storage foundation is properly set up."""
    print("\n" + "="*60)
    print("Artifact Storage Foundation Smoke Test")
    print("="*60)
    
    try:
        # Test 1: Import artifact storage components
        print("\n[Test 1] Importing artifact storage components...")
        from symphainy_platform.foundations.public_works.protocols.artifact_storage_protocol import ArtifactStorageProtocol
        from symphainy_platform.foundations.public_works.abstractions.artifact_storage_abstraction import ArtifactStorageAbstraction
        print("✅ Artifact storage components imported successfully")
        
        # Test 2: Check Public Works integration
        print("\n[Test 2] Checking Public Works integration...")
        from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
        
        # Create Public Works instance (don't initialize - just check structure)
        public_works = PublicWorksFoundationService(config={})
        
        # Check that artifact_storage_abstraction attribute is declared
        if hasattr(public_works, 'artifact_storage_abstraction'):
            print("✅ Public Works has artifact_storage_abstraction attribute declared")
        else:
            print("❌ Public Works missing artifact_storage_abstraction attribute")
            return False
        
        # Check that getter method exists
        if hasattr(public_works, 'get_artifact_storage_abstraction'):
            print("✅ Public Works has get_artifact_storage_abstraction() method")
            
            # Check method signature
            import inspect
            sig = inspect.signature(public_works.get_artifact_storage_abstraction)
            print(f"✅ Method signature: {sig}")
        else:
            print("❌ Public Works missing get_artifact_storage_abstraction() method")
            return False
        
        # Test 3: Verify migration file exists
        print("\n[Test 3] Checking migration file...")
        # Migration is in symphainy_source_code/migrations
        # project_root from test file (parents[3]) is demoversion, so we need symphainy_source_code
        migration_path = project_root / "symphainy_source_code" / "migrations" / "002_add_artifact_support_to_project_files.sql"
        # Also check if project_root is already symphainy_source_code
        if not migration_path.exists():
            migration_path = project_root / "migrations" / "002_add_artifact_support_to_project_files.sql"
        if migration_path.exists():
            print(f"✅ Migration file exists: {migration_path}")
            
            # Check migration content
            migration_content = migration_path.read_text()
            if "artifact_type" in migration_content:
                print("✅ Migration includes artifact_type column")
            else:
                print("❌ Migration missing artifact_type column")
                return False
        else:
            print(f"❌ Migration file not found: {migration_path}")
            return False
        
        # Test 4: Verify artifact storage abstraction structure
        print("\n[Test 4] Verifying artifact storage abstraction methods...")
        required_methods = [
            'store_artifact',
            'get_artifact',
            'list_artifacts',
            'delete_artifact',
            'store_composite_artifact'
        ]
        
        for method_name in required_methods:
            if hasattr(ArtifactStorageAbstraction, method_name):
                print(f"✅ Method exists: {method_name}")
            else:
                print(f"❌ Method missing: {method_name}")
                return False
        
        print("\n" + "="*60)
        print("✅ All smoke tests passed!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run smoke tests."""
    success = await test_artifact_storage_foundation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
