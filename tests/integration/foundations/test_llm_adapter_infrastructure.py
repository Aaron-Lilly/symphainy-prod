"""
Integration Test: LLM Adapter Infrastructure

Validates that LLM adapters and agentic patterns work with REAL LLM CALLS.

This test ensures:
- OpenAI adapter works (real API calls)
- HuggingFace adapter works (real API calls)
- StatelessEmbeddingAgent works (governed access)
- AgentBase._call_llm() works (governed LLM access)

CRITICAL: This test makes REAL API calls and requires valid credentials.
"""

import pytest
import asyncio
from typing import Dict, Any, Optional

from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.public_works.adapters.openai_adapter import OpenAIAdapter
from symphainy_platform.foundations.public_works.adapters.huggingface_adapter import HuggingFaceAdapter
from symphainy_platform.civic_systems.agentic.agents.stateless_embedding_agent import StatelessEmbeddingAgent
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.config.config_helper import (
    get_openai_api_key,
    get_huggingface_endpoint_url,
    get_huggingface_api_key
)


@pytest.fixture
async def public_works():
    """Create and initialize Public Works Foundation Service."""
    config = {}
    foundation = PublicWorksFoundationService(config=config)
    await foundation.initialize()
    yield foundation
    # Cleanup if needed (check if method exists)
    if hasattr(foundation, 'cleanup'):
        await foundation.cleanup()


@pytest.fixture
def execution_context():
    """Create execution context for agents."""
    return ExecutionContext(
        tenant_id="test_tenant",
        user_id="test_user",
        session_id="test_session"
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.llm
class TestLLMAdapterInfrastructure:
    """Test LLM adapter infrastructure with real API calls."""
    
    async def test_openai_adapter_initialization(self, public_works):
        """Test OpenAI adapter initialization."""
        openai_adapter = public_works.get_llm_adapter()
        
        if not openai_adapter:
            pytest.skip("OpenAI adapter not configured (missing API key)")
        
        assert openai_adapter is not None
        assert hasattr(openai_adapter, 'generate_completion')
        assert hasattr(openai_adapter, 'generate_embeddings')
    
    async def test_openai_adapter_real_completion(self, public_works):
        """Test OpenAI adapter with REAL API call."""
        openai_adapter = public_works.get_llm_adapter()
        
        if not openai_adapter:
            pytest.skip("OpenAI adapter not configured (missing API key)")
        
        # Make real API call
        response = await openai_adapter.generate_completion({
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, World!' and nothing else."}
            ],
            "max_tokens": 10,
            "temperature": 0.0
        })
        
        # Validate response
        assert "error" not in response, f"OpenAI API error: {response.get('error')}"
        assert "choices" in response
        assert len(response["choices"]) > 0
        
        content = response["choices"][0]["message"]["content"]
        assert "Hello" in content or "hello" in content.lower()
        
        # Validate usage tracking
        assert "usage" in response
        assert response["usage"]["total_tokens"] > 0
    
    async def test_openai_adapter_real_embeddings(self, public_works):
        """Test OpenAI adapter embeddings with REAL API call."""
        openai_adapter = public_works.get_llm_adapter()
        
        if not openai_adapter:
            pytest.skip("OpenAI adapter not configured (missing API key)")
        
        # Make real API call
        embeddings = await openai_adapter.generate_embeddings(
            text="This is a test sentence for embedding generation.",
            model="text-embedding-ada-002"
        )
        
        # Validate response
        assert len(embeddings) > 0
        assert isinstance(embeddings, list)
        assert all(isinstance(x, float) for x in embeddings)
        assert len(embeddings) == 1536  # text-embedding-ada-002 dimension
    
    async def test_huggingface_adapter_initialization(self, public_works):
        """Test HuggingFace adapter initialization."""
        hf_adapter = public_works.get_huggingface_adapter()
        
        if not hf_adapter:
            pytest.skip("HuggingFace adapter not configured (missing endpoint/API key)")
        
        assert hf_adapter is not None
        assert hasattr(hf_adapter, 'generate_embedding')
        assert hasattr(hf_adapter, 'inference')
    
    async def test_huggingface_adapter_real_embedding(self, public_works):
        """Test HuggingFace adapter with REAL API call."""
        hf_adapter = public_works.get_huggingface_adapter()
        
        if not hf_adapter:
            pytest.skip("HuggingFace adapter not configured (missing endpoint/API key)")
        
        # Make real API call
        result = await hf_adapter.generate_embedding(
            text="This is a test sentence for embedding generation.",
            model="sentence-transformers/all-mpnet-base-v2"
        )
        
        # Validate response
        assert "embedding" in result
        assert "model" in result
        assert "dimension" in result
        
        embedding = result["embedding"]
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
        assert result["dimension"] == len(embedding)
    
    async def test_stateless_embedding_agent_initialization(self, public_works):
        """Test StatelessEmbeddingAgent initialization."""
        hf_adapter = public_works.get_huggingface_adapter()
        
        if not hf_adapter:
            pytest.skip("HuggingFace adapter not configured - cannot test StatelessEmbeddingAgent")
        
        agent = StatelessEmbeddingAgent(
            agent_id="test_embedding_agent",
            public_works=public_works
        )
        
        assert agent is not None
        assert agent.agent_id == "test_embedding_agent"
        assert agent.public_works == public_works
    
    async def test_stateless_embedding_agent_real_embedding(self, public_works, execution_context):
        """Test StatelessEmbeddingAgent with REAL API call."""
        hf_adapter = public_works.get_huggingface_adapter()
        
        if not hf_adapter:
            pytest.skip("HuggingFace adapter not configured - cannot test StatelessEmbeddingAgent")
        
        agent = StatelessEmbeddingAgent(
            agent_id="test_embedding_agent",
            public_works=public_works
        )
        
        # Make real API call via agent (governed access)
        result = await agent.generate_embedding(
            text="This is a test sentence for embedding generation via agent.",
            model="sentence-transformers/all-mpnet-base-v2",
            context=execution_context
        )
        
        # Validate response
        assert "embedding" in result
        assert "model" in result
        assert "dimension" in result
        
        embedding = result["embedding"]
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
    
    async def test_stateless_embedding_agent_process_request(self, public_works, execution_context):
        """Test StatelessEmbeddingAgent.process_request() with REAL API call."""
        hf_adapter = public_works.get_huggingface_adapter()
        
        if not hf_adapter:
            pytest.skip("HuggingFace adapter not configured - cannot test StatelessEmbeddingAgent")
        
        agent = StatelessEmbeddingAgent(
            agent_id="test_embedding_agent",
            public_works=public_works
        )
        
        # Make real API call via process_request
        request = {
            "text": "This is a test sentence for embedding generation via process_request.",
            "model": "sentence-transformers/all-mpnet-base-v2"
        }
        
        response = await agent.process_request(request, execution_context)
        
        # Validate response structure
        assert "artifact_type" in response
        assert response["artifact_type"] == "embedding"
        assert "artifact" in response
        assert "confidence" in response
        
        artifact = response["artifact"]
        assert "embedding" in artifact
        assert "model" in artifact
        assert "dimension" in artifact
    
    async def test_agent_base_call_llm(self, public_works, execution_context):
        """Test AgentBase._call_llm() with REAL API call."""
        openai_adapter = public_works.get_llm_adapter()
        
        if not openai_adapter:
            pytest.skip("OpenAI adapter not configured - cannot test _call_llm()")
        
        # Create a simple agent subclass for testing
        from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
        
        class TestAgent(AgentBase):
            async def process_request(self, request, context):
                return {}
            
            async def get_agent_description(self):
                return "Test agent for _call_llm()"
        
        agent = TestAgent(
            agent_id="test_llm_agent",
            agent_type="test",
            capabilities=["llm_access"],
            public_works=public_works
        )
        
        # Make real API call via _call_llm() (governed access)
        response = await agent._call_llm(
            prompt="Say 'LLM call successful' and nothing else.",
            system_message="You are a test assistant.",
            model="gpt-4o-mini",
            max_tokens=10,
            temperature=0.0
        )
        
        # Validate response
        assert isinstance(response, str)
        assert len(response) > 0
        assert "successful" in response.lower() or "llm" in response.lower()
    
    async def test_agent_base_call_llm_error_handling(self, public_works):
        """Test AgentBase._call_llm() error handling."""
        from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
        
        class TestAgent(AgentBase):
            async def process_request(self, request, context):
                return {}
            
            async def get_agent_description(self):
                return "Test agent"
        
        # Test without Public Works
        agent_no_pw = TestAgent(
            agent_id="test_agent_no_pw",
            agent_type="test",
            capabilities=[],
            public_works=None
        )
        
        with pytest.raises(ValueError, match="Public Works not available"):
            await agent_no_pw._call_llm(
                prompt="Test",
                system_message="Test",
                model="gpt-4o-mini"
            )
        
        # Test with Public Works but no LLM adapter
        # (This would require mocking, but we'll test the real case)
        if not public_works.get_llm_adapter():
            agent_no_adapter = TestAgent(
                agent_id="test_agent_no_adapter",
                agent_type="test",
                capabilities=[],
                public_works=public_works
            )
            
            with pytest.raises(ValueError, match="LLM adapter not available"):
                await agent_no_adapter._call_llm(
                    prompt="Test",
                    system_message="Test",
                    model="gpt-4o-mini"
                )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.llm
class TestLLMAdapterInfrastructureEndToEnd:
    """End-to-end tests for LLM adapter infrastructure."""
    
    async def test_embedding_workflow_end_to_end(self, public_works, execution_context):
        """Test complete embedding workflow: StatelessEmbeddingAgent -> HuggingFaceAdapter."""
        hf_adapter = public_works.get_huggingface_adapter()
        
        if not hf_adapter:
            pytest.skip("HuggingFace adapter not configured")
        
        # Create agent
        agent = StatelessEmbeddingAgent(
            agent_id="e2e_embedding_agent",
            public_works=public_works
        )
        
        # Generate embedding
        test_text = "Insurance policy data: policy_number=12345, premium=1000.00, coverage_type=life"
        result = await agent.generate_embedding(
            text=test_text,
            context=execution_context
        )
        
        # Validate
        assert "embedding" in result
        embedding = result["embedding"]
        assert len(embedding) > 0
        
        # Verify embedding is usable (non-zero vector)
        assert any(abs(x) > 0.001 for x in embedding), "Embedding should not be all zeros"
    
    async def test_llm_workflow_end_to_end(self, public_works, execution_context):
        """Test complete LLM workflow: AgentBase._call_llm() -> OpenAIAdapter."""
        openai_adapter = public_works.get_llm_adapter()
        
        if not openai_adapter:
            pytest.skip("OpenAI adapter not configured")
        
        from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
        
        class TestAgent(AgentBase):
            async def process_request(self, request, context):
                return {}
            
            async def get_agent_description(self):
                return "E2E test agent"
        
        agent = TestAgent(
            agent_id="e2e_llm_agent",
            agent_type="test",
            capabilities=["llm"],
            public_works=public_works
        )
        
        # Make LLM call
        response = await agent._call_llm(
            prompt="Extract the policy number from: 'Policy #12345 has premium $1000'",
            system_message="You are a data extraction assistant. Extract only the requested information.",
            model="gpt-4o-mini",
            max_tokens=20,
            temperature=0.0
        )
        
        # Validate
        assert isinstance(response, str)
        assert "12345" in response or "12345" in response.replace(" ", "")
