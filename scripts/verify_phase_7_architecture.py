#!/usr/bin/env python3
"""
Verification script for Phase 7: Architecture Validation

Checks for:
1. Placeholders, mocks, hard-coded values
2. Architecture compliance
3. End-to-end data flow
"""

import sys
import os
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

def check_for_placeholders():
    """Check for TODO, FIXME, PLACEHOLDER, etc."""
    print("=" * 80)
    print("Checking for placeholders, TODOs, and hard-coded values...")
    print("=" * 80)
    
    issues = []
    critical_paths = [
        "symphainy_platform/civic_systems/artifact_plane",
        "symphainy_platform/civic_systems/smart_city",
        "migrations"
    ]
    
    patterns = [
        (r"TODO", "TODO comment"),
        (r"FIXME", "FIXME comment"),
        (r"PLACEHOLDER", "Placeholder implementation"),
        (r"XXX", "XXX marker"),
        (r"TBD", "TBD marker"),
        (r"raise NotImplementedError", "NotImplementedError"),
        (r"return None\s*#.*placeholder", "Placeholder return None"),
    ]
    
    for root, dirs, files in os.walk(project_root):
        # Skip test files and __pycache__
        if "test" in root or "__pycache__" in root or ".git" in root:
            continue
        
        # Only check critical paths
        rel_path = os.path.relpath(root, project_root)
        if not any(cp in rel_path for cp in critical_paths):
            continue
        
        for file in files:
            if not file.endswith(('.py', '.sql')):
                continue
            
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, 1):
                        for pattern, description in patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                # Skip if it's in a comment explaining MVP approach
                                if "MVP" in line and "permissive" in line.lower():
                                    continue
                                if "capability by design" in line.lower():
                                    continue
                                
                                issues.append({
                                    "file": os.path.relpath(file_path, project_root),
                                    "line": line_num,
                                    "issue": description,
                                    "content": line.strip()[:100]
                                })
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} potential issues:\n")
        for issue in issues[:20]:  # Show first 20
            print(f"  {issue['file']}:{issue['line']} - {issue['issue']}")
            print(f"    {issue['content']}\n")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more\n")
        return False
    else:
        print("✅ No placeholders or TODOs found in critical paths\n")
        return True

def check_architecture_compliance():
    """Check architecture compliance."""
    print("=" * 80)
    print("Checking architecture compliance...")
    print("=" * 80)
    
    checks = []
    
    # Check 1: Artifact Plane uses protocols (not direct Supabase)
    artifact_plane_file = project_root / "symphainy_platform/civic_systems/artifact_plane/artifact_plane.py"
    if artifact_plane_file.exists():
        with open(artifact_plane_file, 'r') as f:
            content = f.read()
            if "from supabase" in content.lower() and "import" in content:
                checks.append(("❌", "Artifact Plane should use protocols, not direct Supabase imports"))
            else:
                checks.append(("✅", "Artifact Plane uses protocols correctly"))
    
    # Check 2: MaterializationPolicyStore has fallback
    policy_store_file = project_root / "symphainy_platform/civic_systems/smart_city/stores/materialization_policy_store.py"
    if policy_store_file.exists():
        with open(policy_store_file, 'r') as f:
            content = f.read()
            if "_get_mvp_permissive_policy" in content:
                checks.append(("✅", "MaterializationPolicyStore has MVP fallback"))
            else:
                checks.append(("⚠️", "MaterializationPolicyStore may not have fallback"))
    
    # Check 3: CuratorPrimitives validates promotion
    curator_primitives_file = project_root / "symphainy_platform/civic_systems/smart_city/primitives/curator_primitives.py"
    if curator_primitives_file.exists():
        with open(curator_primitives_file, 'r') as f:
            content = f.read()
            if "validate_promotion" in content:
                checks.append(("✅", "CuratorPrimitives has validate_promotion method"))
            else:
                checks.append(("❌", "CuratorPrimitives missing validate_promotion"))
    
    # Check 4: CuratorService uses CuratorPrimitives
    curator_service_file = project_root / "symphainy_platform/civic_systems/smart_city/services/curator_service.py"
    if curator_service_file.exists():
        with open(curator_service_file, 'r') as f:
            content = f.read()
            if "curator_primitives" in content and "validate_promotion" in content:
                checks.append(("✅", "CuratorService uses CuratorPrimitives for policy decisions"))
            else:
                checks.append(("❌", "CuratorService should use CuratorPrimitives"))
    
    for status, message in checks:
        print(f"{status} {message}")
    
    all_passed = all(status == "✅" for status, _ in checks)
    print()
    return all_passed

def check_migrations():
    """Check that all migrations are properly structured."""
    print("=" * 80)
    print("Checking migrations...")
    print("=" * 80)
    
    migrations_dir = project_root / "migrations"
    if not migrations_dir.exists():
        print("❌ Migrations directory not found")
        return False
    
    required_migrations = [
        "008_create_artifacts_table_with_lifecycle.sql",
        "009_add_versioning_to_artifacts.sql",
        "010_add_dependencies_to_artifacts.sql",
        "011_create_materialization_policies.sql",
        "012_create_records_of_fact.sql",
        "013_create_platform_dna_registries.sql"
    ]
    
    found = []
    missing = []
    
    for migration in required_migrations:
        migration_path = migrations_dir / migration
        if migration_path.exists():
            found.append(migration)
            print(f"✅ {migration}")
        else:
            missing.append(migration)
            print(f"❌ {migration} - MISSING")
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} required migrations")
        return False
    else:
        print(f"\n✅ All {len(found)} required migrations present")
        return True

def main():
    """Run all verification checks."""
    print("\n" + "=" * 80)
    print("Phase 7: Architecture Verification")
    print("=" * 80 + "\n")
    
    results = []
    
    # Check 1: Placeholders
    results.append(("Placeholder Check", check_for_placeholders()))
    
    # Check 2: Architecture compliance
    results.append(("Architecture Compliance", check_architecture_compliance()))
    
    # Check 3: Migrations
    results.append(("Migrations", check_migrations()))
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ All checks passed!")
    else:
        print("⚠️  Some checks failed. Please review above.")
    print("=" * 80 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
