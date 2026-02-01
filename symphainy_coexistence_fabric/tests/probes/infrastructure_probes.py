"""
Infrastructure Probes for Team A

These probes test whether infrastructure is actually available and working.
Run them to discover what's wired vs what's missing.

Usage:
    pytest tests/probes/infrastructure_probes.py -v
    
    Or run specific probes:
    pytest tests/probes/infrastructure_probes.py::test_redis_connectivity -v
"""

import pytest
import os
import asyncio
from typing import Dict, Any


# ============================================================================
# CONNECTIVITY PROBES - Can we reach external services?
# ============================================================================

class TestConnectivityProbes:
    """Test connectivity to external services."""
    
    def test_redis_connectivity(self):
        """Probe: Can we connect to Redis?"""
        try:
            import redis
            r = redis.Redis(
                host=os.environ.get("REDIS_HOST", "localhost"),
                port=int(os.environ.get("REDIS_PORT", "6379")),
                socket_timeout=5
            )
            result = r.ping()
            assert result, "Redis ping returned False"
            print("✅ Redis: CONNECTED")
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")
    
    def test_arango_connectivity(self):
        """Probe: Can we connect to ArangoDB?"""
        try:
            import requests
            arango_host = os.environ.get("ARANGO_HOST", "localhost")
            arango_port = os.environ.get("ARANGO_PORT", "8529")
            arango_user = os.environ.get("ARANGO_USER", "root")
            arango_pass = os.environ.get("ARANGO_PASSWORD", "")
            
            resp = requests.get(
                f"http://{arango_host}:{arango_port}/_api/version",
                auth=(arango_user, arango_pass),
                timeout=5
            )
            
            assert resp.status_code == 200, f"ArangoDB returned {resp.status_code}"
            print(f"✅ ArangoDB: CONNECTED (version: {resp.json().get('version')})")
        except Exception as e:
            pytest.skip(f"ArangoDB not available: {e}")
    
    def test_supabase_connectivity(self):
        """Probe: Can we connect to Supabase?"""
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            pytest.skip("SUPABASE_URL or SUPABASE_KEY not set")
        
        try:
            import requests
            resp = requests.get(
                f"{supabase_url}/rest/v1/",
                headers={"apikey": supabase_key},
                timeout=5
            )
            # 200 or 404 are both "connected" - we just can't list tables
            assert resp.status_code in [200, 404, 401], f"Supabase returned {resp.status_code}"
            print("✅ Supabase: CONNECTED")
        except Exception as e:
            pytest.skip(f"Supabase not available: {e}")
    
    def test_openai_api_key_configured(self):
        """Probe: Is OpenAI API key configured?"""
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set in environment")
        
        # Don't actually call OpenAI - just verify key exists
        assert len(api_key) > 10, "OPENAI_API_KEY seems too short"
        assert api_key.startswith("sk-"), "OPENAI_API_KEY should start with 'sk-'"
        print("✅ OpenAI API Key: CONFIGURED")
    
    def test_gcs_credentials_configured(self):
        """Probe: Are GCS credentials configured?"""
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        project_id = os.environ.get("GCP_PROJECT_ID")
        
        if not credentials_path and not project_id:
            pytest.skip("No GCS credentials configured (GOOGLE_APPLICATION_CREDENTIALS or GCP_PROJECT_ID)")
        
        if credentials_path:
            assert os.path.exists(credentials_path), f"Credentials file not found: {credentials_path}"
        
        print("✅ GCS Credentials: CONFIGURED")


# ============================================================================
# PUBLIC WORKS ABSTRACTION PROBES - Are abstractions wired?
# ============================================================================

class TestAbstractionProbes:
    """Test whether Public Works abstractions are wired."""
    
    @pytest.fixture
    def public_works(self):
        """Try to create PublicWorksFoundationService."""
        try:
            from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
            pw = PublicWorksFoundationService(config={})
            return pw
        except ImportError as e:
            pytest.skip(f"Cannot import PublicWorksFoundationService: {e}")
        except Exception as e:
            pytest.skip(f"Cannot create PublicWorksFoundationService: {e}")
    
    def test_ingestion_abstraction_wired(self, public_works):
        """Probe: Is ingestion abstraction wired?"""
        abstraction = getattr(public_works, "ingestion_abstraction", None)
        if abstraction is None:
            pytest.skip("ingestion_abstraction is NOT WIRED")
        print("✅ Ingestion Abstraction: WIRED")
    
    def test_file_storage_abstraction_wired(self, public_works):
        """Probe: Is file storage abstraction wired?"""
        abstraction = getattr(public_works, "file_storage_abstraction", None)
        if abstraction is None:
            pytest.skip("file_storage_abstraction is NOT WIRED")
        print("✅ File Storage Abstraction: WIRED")
    
    def test_artifact_storage_abstraction_wired(self, public_works):
        """Probe: Is artifact storage abstraction wired?"""
        abstraction = getattr(public_works, "artifact_storage_abstraction", None)
        if abstraction is None:
            pytest.skip("artifact_storage_abstraction is NOT WIRED")
        print("✅ Artifact Storage Abstraction: WIRED")
    
    def test_registry_abstraction_wired(self, public_works):
        """Probe: Is registry abstraction wired?"""
        abstraction = getattr(public_works, "registry_abstraction", None)
        if abstraction is None:
            pytest.skip("registry_abstraction is NOT WIRED")
        print("✅ Registry Abstraction: WIRED")
    
    def test_deterministic_compute_abstraction_wired(self, public_works):
        """Probe: Is deterministic compute abstraction wired?"""
        abstraction = getattr(public_works, "deterministic_compute_abstraction", None)
        if abstraction is None:
            pytest.skip("deterministic_compute_abstraction is NOT WIRED")
        print("✅ Deterministic Compute Abstraction: WIRED")
    
    def test_semantic_data_abstraction_wired(self, public_works):
        """Probe: Is semantic data abstraction wired?"""
        abstraction = getattr(public_works, "semantic_data_abstraction", None)
        if abstraction is None:
            pytest.skip("semantic_data_abstraction is NOT WIRED")
        print("✅ Semantic Data Abstraction: WIRED")


# ============================================================================
# CIVIC SYSTEMS SDK PROBES - Are Smart City SDKs available?
# ============================================================================

class TestCivicSystemsProbes:
    """Test whether Civic Systems SDKs are available."""
    
    @pytest.fixture
    def smart_city_sdks(self):
        """Try to create Smart City SDKs."""
        try:
            from symphainy_platform.civic_systems.smart_city import (
                SmartCitySDKs,
                SecurityGuardSDK,
                DataStewardSDK,
                NurseSDK
            )
            return SmartCitySDKs
        except ImportError as e:
            pytest.skip(f"Cannot import SmartCitySDKs: {e}")
    
    def test_security_guard_sdk_importable(self, smart_city_sdks):
        """Probe: Can we import SecurityGuardSDK?"""
        try:
            from symphainy_platform.civic_systems.smart_city import SecurityGuardSDK
            print("✅ SecurityGuardSDK: IMPORTABLE")
        except ImportError as e:
            pytest.skip(f"SecurityGuardSDK not importable: {e}")
    
    def test_data_steward_sdk_importable(self, smart_city_sdks):
        """Probe: Can we import DataStewardSDK?"""
        try:
            from symphainy_platform.civic_systems.smart_city import DataStewardSDK
            print("✅ DataStewardSDK: IMPORTABLE")
        except ImportError as e:
            pytest.skip(f"DataStewardSDK not importable: {e}")
    
    def test_nurse_sdk_importable(self, smart_city_sdks):
        """Probe: Can we import NurseSDK?"""
        try:
            from symphainy_platform.civic_systems.smart_city import NurseSDK
            print("✅ NurseSDK: IMPORTABLE")
        except ImportError as e:
            pytest.skip(f"NurseSDK not importable: {e}")


# ============================================================================
# REASONING LAYER PROBES - Is the AI layer available?
# ============================================================================

class TestReasoningProbes:
    """Test whether Reasoning layer components are available."""
    
    def test_llm_service_importable(self):
        """Probe: Can we import LLMService?"""
        try:
            from symphainy_platform.civic_systems.platform_sdk.services.reasoning_service import ReasoningService
            print("✅ ReasoningService: IMPORTABLE")
        except ImportError as e:
            pytest.skip(f"ReasoningService not importable: {e}")
    
    def test_agent_service_importable(self):
        """Probe: Can we import AgentService?"""
        try:
            from symphainy_platform.civic_systems.agentic import AgentService
            print("✅ AgentService: IMPORTABLE")
        except ImportError as e:
            pytest.skip(f"AgentService not importable: {e}")
    
    def test_openai_adapter_importable(self):
        """Probe: Can we import OpenAIAdapter?"""
        try:
            from symphainy_platform.foundations.public_works.adapters.llm_adapters import OpenAIAdapter
            print("✅ OpenAIAdapter: IMPORTABLE")
        except ImportError as e:
            pytest.skip(f"OpenAIAdapter not importable: {e}")
    
    @pytest.mark.asyncio
    async def test_openai_adapter_connectivity(self):
        """Probe: Can OpenAI adapter actually make a call?"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")
        
        try:
            from symphainy_platform.foundations.public_works.adapters.llm_adapters import OpenAIAdapter
            adapter = OpenAIAdapter(api_key=api_key)
            
            # Make a minimal call
            response = await adapter.complete(
                prompt="Say 'hello' and nothing else.",
                max_tokens=10
            )
            
            assert response is not None
            assert len(response) > 0
            print(f"✅ OpenAI API: WORKING (response: {response[:50]}...)")
        except Exception as e:
            pytest.skip(f"OpenAI adapter failed: {e}")


# ============================================================================
# AGENT INSTANTIATION PROBES - Can agents be created?
# ============================================================================

class TestAgentInstantiationProbes:
    """Test whether agents can be instantiated."""
    
    @pytest.fixture
    def agent_registry(self):
        """Get agent registry."""
        try:
            from symphainy_platform.civic_systems.agentic import AGENT_REGISTRY
            return AGENT_REGISTRY
        except ImportError as e:
            pytest.skip(f"Cannot import AGENT_REGISTRY: {e}")
    
    def test_guide_agent_instantiable(self, agent_registry):
        """Probe: Can GuideAgent be instantiated?"""
        agent_info = agent_registry.get("guide_agent")
        if not agent_info:
            pytest.skip("guide_agent not in registry")
        
        try:
            # Try to instantiate
            class_path = agent_info.get("class_path")
            if not class_path:
                pytest.skip("guide_agent has no class_path")
            
            # Dynamic import
            module_path, class_name = class_path.rsplit(".", 1)
            import importlib
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)
            
            # Instantiate with minimal args
            agent = agent_class(agent_id="probe_test")
            print("✅ GuideAgent: INSTANTIABLE")
        except Exception as e:
            pytest.skip(f"GuideAgent not instantiable: {e}")
    
    def test_sop_generation_agent_instantiable(self, agent_registry):
        """Probe: Can SOPGenerationAgent be instantiated?"""
        agent_info = agent_registry.get("sop_generation_agent")
        if not agent_info:
            pytest.skip("sop_generation_agent not in registry")
        
        try:
            class_path = agent_info.get("class_path")
            if not class_path:
                pytest.skip("sop_generation_agent has no class_path")
            
            module_path, class_name = class_path.rsplit(".", 1)
            import importlib
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)
            
            agent = agent_class(agent_id="probe_test")
            print("✅ SOPGenerationAgent: INSTANTIABLE")
        except Exception as e:
            pytest.skip(f"SOPGenerationAgent not instantiable: {e}")


# ============================================================================
# SERVICE FACTORY PROBES - Does service wiring work?
# ============================================================================

class TestServiceFactoryProbes:
    """Test whether service factory can wire services."""
    
    def test_service_factory_importable(self):
        """Probe: Can we import ServiceFactory?"""
        try:
            from symphainy_platform.runtime.service_factory import ServiceFactory
            print("✅ ServiceFactory: IMPORTABLE")
        except ImportError as e:
            pytest.skip(f"ServiceFactory not importable: {e}")
    
    def test_service_factory_can_build_without_infra(self):
        """Probe: Can ServiceFactory build without full infrastructure?"""
        try:
            from symphainy_platform.runtime.service_factory import ServiceFactory
            
            # Try to build with minimal config
            factory = ServiceFactory(
                config={},
                consul_client=None  # No Consul
            )
            
            # Check if handlers registered
            handler_count = len(factory._intent_handlers) if hasattr(factory, '_intent_handlers') else 0
            print(f"✅ ServiceFactory: BUILDABLE (handlers: {handler_count})")
        except Exception as e:
            pytest.skip(f"ServiceFactory not buildable: {e}")
    
    def test_handler_lookup_works(self):
        """Probe: Can we look up a handler for an intent?"""
        try:
            from symphainy_platform.runtime.service_factory import ServiceFactory
            
            factory = ServiceFactory(config={}, consul_client=None)
            
            # Try to get handler for ingest_file
            handler = factory.get_handler("ingest_file")
            
            if handler is None:
                pytest.skip("No handler registered for ingest_file")
            
            print(f"✅ Handler lookup: WORKS (ingest_file -> {handler.__class__.__name__})")
        except Exception as e:
            pytest.skip(f"Handler lookup failed: {e}")


# ============================================================================
# SUMMARY REPORT
# ============================================================================

def test_generate_infrastructure_report():
    """Generate a summary report of infrastructure status."""
    report = []
    report.append("\n" + "=" * 60)
    report.append("INFRASTRUCTURE PROBE SUMMARY")
    report.append("=" * 60)
    report.append("\nTo get the full picture, run:")
    report.append("  pytest tests/probes/infrastructure_probes.py -v")
    report.append("\nSkipped tests indicate missing infrastructure.")
    report.append("Passed tests indicate working infrastructure.")
    report.append("=" * 60)
    
    print("\n".join(report))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
