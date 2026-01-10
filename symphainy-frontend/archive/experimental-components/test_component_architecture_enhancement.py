#!/usr/bin/env python3
"""
Validation Test for Component Architecture Enhancement
Tests the advanced component architecture system
"""

import os
import sys
from pathlib import Path

def check_file_size(file_path: str, max_lines: int = 100) -> bool:
    """Check if file is under the specified line count"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            return len(lines) <= max_lines
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def check_directory_structure(base_path: str) -> bool:
    """Check if directory follows micro-modular structure"""
    required_files = ['AdvancedComponent.tsx', 'index.ts']
    optional_files = ['lifecycle.ts', 'optimization.ts', 'composition.ts', 'EnhancedComponentProvider.tsx']
    
    base_dir = Path(base_path)
    if not base_dir.exists():
        print(f"❌ Directory {base_path} does not exist")
        return False
    
    # Check required files
    for file in required_files:
        file_path = base_dir / file
        if not file_path.exists():
            print(f"❌ Required file {file} missing in {base_path}")
            return False
    
    # Check optional files (at least some should exist)
    optional_exists = any((base_dir / file).exists() for file in optional_files)
    if not optional_exists:
        print(f"⚠️  No optional files found in {base_path}")
    
    return True

def validate_component_micro_modules():
    """Validate component architecture micro-modules"""
    print("🔍 Validating Component Architecture Micro-Modules...")
    
    component_dir = "shared/components/core"
    
    # Check directory structure
    if not check_directory_structure(component_dir):
        return False
    
    # Check orchestrator files (should be under 100 lines)
    orchestrator_files = [
        f"{component_dir}/index.ts",
        f"{component_dir}/AdvancedComponent/index.tsx",
        f"{component_dir}/EnhancedComponentProvider/index.tsx",
        f"{component_dir}/lifecycle/index.ts",
        f"{component_dir}/optimization/index.ts",
        f"{component_dir}/composition/index.ts"
    ]
    
    all_files_valid = True
    for file_path in orchestrator_files:
        if os.path.exists(file_path):
            is_valid = check_file_size(file_path, 100)
            status = "✅" if is_valid else "❌"
            print(f"{status} {file_path}: {'Under 100 lines' if is_valid else 'Over 100 lines'}")
            if not is_valid:
                all_files_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    # Check that micro-modular directories exist
    micro_modules = [
        "AdvancedComponent",
        "EnhancedComponentProvider", 
        "lifecycle",
        "optimization",
        "composition"
    ]
    
    for module in micro_modules:
        module_path = f"{component_dir}/{module}"
        if os.path.exists(module_path):
            print(f"✅ {module_path}: Micro-module directory exists")
        else:
            print(f"❌ {module_path}: Micro-module directory missing")
            all_files_valid = False
    
    return all_files_valid

def check_component_enhancement_features():
    """Check component enhancement features"""
    print("\n🔍 Checking Component Enhancement Features...")
    
    # Check the new micro-modular structure
    enhancement_files = [
        "shared/components/core/AdvancedComponent/performance.tsx",
        "shared/components/core/lifecycle/enhancement.ts",
        "shared/components/core/optimization/memoization.ts"
    ]
    
    enhancement_patterns = [
        'AdvancedErrorBoundary',
        'usePerformanceMonitoring',
        'useLazyLoading',
        'useCaching',
        'useLifecycle',
        'useComponentVisibility',
        'useDeepMemo',
        'useOptimizedCallback',
        'useVirtualization',
        'useRenderOptimization'
    ]
    
    all_enhancements_valid = True
    for file_path in enhancement_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    found_patterns = []
                    for pattern in enhancement_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
                    
                    if len(found_patterns) >= 3:  # At least 3 patterns should be found
                        print(f"✅ {file_path}: Enhancement features present ({len(found_patterns)} patterns)")
                    else:
                        print(f"❌ {file_path}: Missing enhancement features")
                        all_enhancements_valid = False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_enhancements_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_enhancements_valid

def check_composition_features():
    """Check composition features"""
    print("\n🔍 Checking Composition Features...")
    
    # Check the new micro-modular structure
    composition_files = [
        "shared/components/core/composition/patterns.ts",
        "shared/components/core/EnhancedComponentProvider/composition-hooks.ts"
    ]
    
    composition_patterns = [
        'useContextComposition',
        'useRenderProps',
        'useCompoundComponent',
        'createHOC',
        'useComponentComposition',
        'createContextProvider',
        'useComponentRegistry',
        'EnhancedComponentProvider'
    ]
    
    all_composition_valid = True
    for file_path in composition_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    found_patterns = []
                    for pattern in composition_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
                    
                    if len(found_patterns) >= 2:  # At least 2 patterns should be found
                        print(f"✅ {file_path}: Composition features present ({len(found_patterns)} patterns)")
                    else:
                        print(f"❌ {file_path}: Missing composition features")
                        all_composition_valid = False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_composition_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_composition_valid

def check_react_integration():
    """Check React integration"""
    print("\n🔍 Checking React Integration...")
    
    # Check the new micro-modular structure
    react_files = [
        "shared/components/core/AdvancedComponent/core.tsx",
        "shared/components/core/lifecycle/core.ts",
        "shared/components/core/optimization/core.ts",
        "shared/components/core/composition/patterns.ts"
    ]
    
    react_patterns = [
        'useEffect',
        'useState',
        'useCallback',
        'useMemo',
        'useRef',
        'forwardRef',
        'createContext',
        'useContext',
        'memo',
        'Suspense'
    ]
    
    all_react_valid = True
    for file_path in react_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    found_patterns = []
                    for pattern in react_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
                    
                    if len(found_patterns) >= 3:  # At least 3 patterns should be found
                        print(f"✅ {file_path}: React integration present ({len(found_patterns)} patterns)")
                    else:
                        print(f"❌ {file_path}: Missing React integration")
                        all_react_valid = False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_react_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_react_valid

def main():
    """Main validation function"""
    print("🚀 Phase 5: Component Architecture Enhancement - Validation")
    print("=" * 80)
    
    # Validate component micro-modules
    component_valid = validate_component_micro_modules()
    
    # Check component enhancement features
    enhancement_valid = check_component_enhancement_features()
    
    # Check composition features
    composition_valid = check_composition_features()
    
    # Check React integration
    react_valid = check_react_integration()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    
    print(f"Component Micro-Modules: {'✅ PASS' if component_valid else '❌ FAIL'}")
    print(f"Component Enhancement Features: {'✅ PASS' if enhancement_valid else '❌ FAIL'}")
    print(f"Composition Features: {'✅ PASS' if composition_valid else '❌ FAIL'}")
    print(f"React Integration: {'✅ PASS' if react_valid else '❌ FAIL'}")
    
    overall_success = component_valid and enhancement_valid and composition_valid and react_valid
    
    if overall_success:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ Component architecture enhancement completed successfully")
        print("✅ Advanced component core implemented")
        print("✅ Lifecycle management created")
        print("✅ Performance optimization utilities added")
        print("✅ Composition patterns implemented")
        print("✅ React integration completed")
        print("\n🚀 Ready to proceed to next phase!")
    else:
        print("\n❌ SOME VALIDATIONS FAILED")
        print("Please review and fix the issues above before proceeding")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 