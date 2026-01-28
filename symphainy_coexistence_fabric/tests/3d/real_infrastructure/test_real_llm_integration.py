"""
Test Real LLM Integration

Functional Tests: Validate that LLM calls actually work (if services use LLMs).
These tests catch: API key issues, rate limits, response quality, etc.
"""

import pytest
import sys
import os
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def _has_llm_api_key():
    """Check if LLM API key is available."""
    openai_key = os.getenv("LLM_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("LLM_ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    return bool(openai_key or anthropic_key)


class TestRealLLMConnectivity:
    """Test real LLM API connectivity."""
    
    @pytest.mark.real_infrastructure
    @pytest.mark.functional
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_llm_api_key_configured(self):
        """Test that LLM API key is configured."""
        if not _has_llm_api_key():
            pytest.skip("LLM API keys not configured (set LLM_OPENAI_API_KEY or LLM_ANTHROPIC_API_KEY)")
        
        assert True, "LLM API key is configured"
    
    @pytest.mark.real_infrastructure
    @pytest.mark.functional
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_real_llm_call_works(self, real_public_works):
        """Test that real LLM API calls work."""
        if not _has_llm_api_key():
            pytest.skip("LLM API keys not configured")
        
        if not hasattr(real_public_works, 'llm_abstraction') or not real_public_works.llm_abstraction:
            pytest.skip("LLM abstraction not available")
        
        # Make a real LLM call
        from symphainy_platform.foundations.public_works.abstractions.llm_abstraction import LLMAbstraction
        from symphainy_platform.foundations.public_works.protocols.llm_protocol import LLMRequest
        
        llm = real_public_works.llm_abstraction
        
        request = LLMRequest(
            messages=[{"role": "user", "content": "Say 'test successful' if you can read this."}],
            model="gpt-3.5-turbo",  # Use cheapest model
            max_tokens=50
        )
        
        try:
            response = await llm.generate_response(request)
            
            # Should get a response
            assert response is not None, "LLM should return a response"
            
            # Response should have content
            if hasattr(response, 'content'):
                assert len(response.content) > 0, "LLM response should have content"
                assert "test" in response.content.lower() or "successful" in response.content.lower(), \
                    f"LLM should respond meaningfully. Got: {response.content}"
        except Exception as e:
            pytest.fail(f"Real LLM call failed: {e}")


class TestRealGuideAgentLLM:
    """Test GuideAgent with real LLM - catches 'agents just echo' issues."""
    
    @pytest.mark.real_infrastructure
    @pytest.mark.functional
    @pytest.mark.critical
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_guide_agent_uses_real_llm(self, real_solutions, real_execution_context):
        """Test that GuideAgent actually uses LLM, not just echo."""
        if not _has_llm_api_key():
            pytest.skip("LLM API keys not configured")
        
        solutions = await real_solutions
        context = await real_execution_context
        coexistence_solution = solutions.coexistence
        
        journey = coexistence_solution.get_journey("guide_agent")
        if not journey:
            pytest.skip("GuideAgent journey not available")
        
        # Ask a question that requires LLM understanding
        test_message = "What is 2 + 2? Answer with just the number."
        
        result = await journey.compose_journey(
            context=context,
            journey_params={
                "action": "process_message",
                "message": test_message
            }
        )
        
        if "artifacts" in result:
            response_text = str(result["artifacts"]).lower()
            
            # Should contain "4" (shows LLM actually processed the question)
            assert "4" in response_text, \
                f"GuideAgent should use LLM to answer. Got: {response_text[:200]}"
            
            # Should not just echo the question
            assert test_message.lower() not in response_text or \
                   len(response_text) > len(test_message) * 1.5, \
                "GuideAgent should generate response, not echo"
