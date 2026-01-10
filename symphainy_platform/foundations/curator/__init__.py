"""
Curator Foundation

Capability registry for the platform.
Curator is NOT execution - it's the platform's capability ontology.

Responsibilities:
- Registers capabilities
- Describes: inputs, outputs, determinism, owning realm
- Provides lookup: intent → capability

Runtime executes the capability, Curator just registers/looks up.
"""
