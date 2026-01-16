"""
Quick Verification Script for Phase 1 & 2

Verifies that Phase 1 & 2 components are properly implemented and can be imported.

Usage:
    python3 scripts/verify_phase1_2.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def verify_imports():
    """Verify all Phase 1 & 2 imports work."""
    print("=" * 60)
    print("Phase 1 & 2 Import Verification")
    print("=" * 60)
    
    errors = []
    
    # Phase 1: Data Quality
    print("\n📊 Phase 1: Data Quality")
    try:
        from symphainy_platform.realms.insights.enabling_services.data_quality_service import DataQualityService
        print("  ✅ DataQualityService")
    except Exception as e:
        print(f"  ❌ DataQualityService: {e}")
        errors.append(f"DataQualityService: {e}")
    
    # Phase 2: Guide Registry
    print("\n📚 Phase 2: Guide Registry")
    try:
        from symphainy_platform.civic_systems.platform_sdk.guide_registry import GuideRegistry
        print("  ✅ GuideRegistry")
    except Exception as e:
        print(f"  ❌ GuideRegistry: {e}")
        errors.append(f"GuideRegistry: {e}")
    
    # Phase 2: Semantic Self Discovery
    print("\n🔍 Phase 2: Semantic Self Discovery")
    try:
        from symphainy_platform.realms.insights.enabling_services.semantic_self_discovery_service import SemanticSelfDiscoveryService
        print("  ✅ SemanticSelfDiscoveryService")
    except Exception as e:
        print(f"  ❌ SemanticSelfDiscoveryService: {e}")
        errors.append(f"SemanticSelfDiscoveryService: {e}")
    
    # Phase 2: Guided Discovery
    print("\n🎯 Phase 2: Guided Discovery")
    try:
        from symphainy_platform.realms.insights.enabling_services.guided_discovery_service import GuidedDiscoveryService
        print("  ✅ GuidedDiscoveryService")
    except Exception as e:
        print(f"  ❌ GuidedDiscoveryService: {e}")
        errors.append(f"GuidedDiscoveryService: {e}")
    
    # Orchestrator
    print("\n🎼 Orchestrator")
    try:
        from symphainy_platform.realms.insights.orchestrators.insights_orchestrator import InsightsOrchestrator
        print("  ✅ InsightsOrchestrator")
        
        # Check if Phase 2 services are initialized
        orchestrator = InsightsOrchestrator()
        if hasattr(orchestrator, 'semantic_self_discovery_service'):
            print("  ✅ Phase 2 services initialized")
        else:
            print("  ❌ Phase 2 services NOT initialized")
            errors.append("Phase 2 services not initialized in orchestrator")
        
        if hasattr(orchestrator, 'guided_discovery_service'):
            print("  ✅ Guided discovery service initialized")
        else:
            print("  ❌ Guided discovery service NOT initialized")
            errors.append("Guided discovery service not initialized")
            
    except Exception as e:
        print(f"  ❌ InsightsOrchestrator: {e}")
        errors.append(f"InsightsOrchestrator: {e}")
    
    # Realm
    print("\n🏛️  Realm")
    try:
        from symphainy_platform.realms.insights.insights_realm import InsightsRealm
        print("  ✅ InsightsRealm")
        
        # Check intent declarations
        realm = InsightsRealm()
        intents = realm.declare_intents()
        
        required_intents = [
            "assess_data_quality",  # Phase 1
            "interpret_data_self_discovery",  # Phase 2
            "interpret_data_guided"  # Phase 2
        ]
        
        missing_intents = [intent for intent in required_intents if intent not in intents]
        if missing_intents:
            print(f"  ❌ Missing intent declarations: {missing_intents}")
            errors.append(f"Missing intent declarations: {missing_intents}")
        else:
            print("  ✅ All Phase 1 & 2 intents declared")
            
    except Exception as e:
        print(f"  ❌ InsightsRealm: {e}")
        errors.append(f"InsightsRealm: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if errors:
        print("❌ VERIFICATION FAILED")
        print(f"\nErrors found: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ VERIFICATION PASSED")
        print("\nAll Phase 1 & 2 components are properly implemented!")
        return True


def verify_orchestrator_handlers():
    """Verify orchestrator has Phase 2 handlers."""
    print("\n" + "=" * 60)
    print("Orchestrator Handler Verification")
    print("=" * 60)
    
    try:
        from symphainy_platform.realms.insights.orchestrators.insights_orchestrator import InsightsOrchestrator
        
        orchestrator = InsightsOrchestrator()
        
        # Check for Phase 2 handlers
        handlers = {
            "_handle_self_discovery": "interpret_data_self_discovery",
            "_handle_guided_discovery": "interpret_data_guided",
            "_get_embeddings": "embeddings helper"
        }
        
        all_present = True
        for handler_name, description in handlers.items():
            if hasattr(orchestrator, handler_name):
                print(f"  ✅ {handler_name} ({description})")
            else:
                print(f"  ❌ {handler_name} ({description}) - MISSING")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"  ❌ Error checking handlers: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Phase 1 & 2 Verification Script")
    print("=" * 60)
    
    # Verify imports
    imports_ok = verify_imports()
    
    # Verify handlers
    handlers_ok = verify_orchestrator_handlers()
    
    # Final summary
    print("\n" + "=" * 60)
    if imports_ok and handlers_ok:
        print("✅ ALL VERIFICATIONS PASSED")
        print("\nPhase 1 & 2 are ready for testing!")
        print("\nNext steps:")
        print("  1. Seed default guides in Supabase")
        print("  2. Run E2E tests for Phase 1 & 2")
        print("  3. Proceed with Phase 3 implementation")
        sys.exit(0)
    else:
        print("❌ VERIFICATION FAILED")
        print("\nPlease fix the errors above before proceeding.")
        sys.exit(1)
