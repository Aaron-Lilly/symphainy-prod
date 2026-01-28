"""
Content Enabling Services - DEPRECATED

All content enabling services have been moved to foundations/libraries or civic_systems/agentic:
- FileParserService -> foundations/libraries/parsing/
- DeterministicEmbeddingService -> foundations/libraries/embeddings/
- DeterministicChunkingService -> foundations/libraries/chunking/
- SemanticProfileRegistry -> foundations/libraries/registries/
- SemanticTriggerBoundary -> foundations/libraries/governance/
- EmbeddingService -> civic_systems/agentic/agents/embedding_agent.py
- SemanticSignalExtractor -> civic_systems/agentic/agents/semantic_signal_extractor.py

Import from foundations.libraries instead:
  from symphainy_platform.foundations.libraries.parsing import FileParserService
  from symphainy_platform.foundations.libraries.embeddings import DeterministicEmbeddingService
  etc.
"""

# This directory is kept for backward compatibility but should not be used.
# All services have been moved to their canonical locations.

__all__ = []
