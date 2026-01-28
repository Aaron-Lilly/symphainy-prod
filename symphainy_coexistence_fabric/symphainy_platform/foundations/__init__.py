"""
Symphainy Foundations

Foundations provide platform primitives:
- Public Works: Infrastructure abstractions (adapters, abstractions, IO, infra bindings)
- Libraries: Pure algorithmic capabilities (parsing, chunking, embeddings, matching, etc.)
- Curator: Capability registry (intent → capability lookup)

Libraries Organization:
- parsing/       - File parsing capabilities
- chunking/      - Deterministic chunking
- embeddings/    - Embedding generation
- matching/      - Schema and semantic matching
- validation/    - Pattern validation
- metrics/       - Metrics calculation
- quality/       - Data quality assessment
- coexistence/   - Coexistence analysis and blueprints
- export/        - Export and migration capabilities
- extraction/    - Structured data extraction
- visualization/ - Visual generation (diagrams, charts)
- reporting/     - Report generation
- workflow/      - Workflow conversion
- governance/    - Governance enforcement
- registries/    - Profile and config registries
"""

# Libraries are imported on-demand to avoid circular imports
# Use: from symphainy_platform.foundations.libraries.parsing import FileParserService
