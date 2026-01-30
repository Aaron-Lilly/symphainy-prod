#!/usr/bin/env python3
"""
Probe 04: Public Works (Foundations)

TRACES (does not assert):
- What adapters exist; which are wired at boot; which are used
- 5-layer pattern in code (Layer 0 adapters, Layer 1 abstractions, etc.)
- Who calls PublicWorks and what they use

Output: Public Works Reality Map (for docs/testing/reality_maps/ or paste into report).
Run from repo root: python3 probes/probe_04_public_works.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def trace_adapters():
    """List Layer 0 adapters from PublicWorksFoundationService.__init__."""
    pw = REPO_ROOT / "symphainy_platform" / "foundations" / "public_works" / "foundation_service.py"
    text = pw.read_text()
    adapters = []
    for line in text.splitlines():
        if "self." in line and "_adapter:" in line and "Optional" in line:
            name = line.strip().split("self.")[1].split(":")[0].strip()
            adapters.append(name)
    return adapters


def trace_abstractions():
    """List Layer 1 abstractions from PublicWorksFoundationService.__init__."""
    pw = REPO_ROOT / "symphainy_platform" / "foundations" / "public_works" / "foundation_service.py"
    text = pw.read_text()
    abstractions = []
    for line in text.splitlines():
        if "self." in line and "_abstraction:" in line and "Optional" in line:
            name = line.strip().split("self.")[1].split(":")[0].strip()
            abstractions.append(name)
    return abstractions


def trace_callers():
    """Who uses public_works / PublicWorksFoundationService (from grep evidence)."""
    return [
        ("service_factory.py", "create_runtime_services", "public_works = PublicWorksFoundationService(config); get_state_abstraction(), get_file_storage_abstraction(), get_redis_adapter(), get_registry_abstraction(), get_artifact_storage_abstraction() passed to StateSurface, WAL, ELM, RuntimeServices"),
        ("state_surface.py", "StateSurface", "state_abstraction (StateManagementProtocol) from Public Works; used for retrieve_state, store_state"),
        ("agent_base.py", "AgentBase", "public_works.get_llm_adapter()"),
    ]


def main():
    print("# Probe 04 Output: Public Works Reality Map (draft)\n")
    print("## Adapters (Layer 0) – declared\n")
    for a in trace_adapters():
        print(f"- {a}")
    print("\n## Abstractions (Layer 1) – declared\n")
    for a in trace_abstractions():
        print(f"- {a}")
    print("\n## 5-layer pattern (evidence)\n")
    print("- **Layer 0:** Adapters created in _create_adapters() (foundation_service.py); config-driven (redis, consul, parsing, meilisearch, etc.).")
    print("- **Layer 1:** Abstractions created in _create_abstractions(); wrap adapters.")
    print("- **Layer 2:** Protocols (StateManagementProtocol, etc.) – see foundations/public_works/protocols/.")
    print("- **Layer 3/4:** Foundation service orchestrates; initialize() calls _create_adapters then _create_abstractions.")
    print("\n## Callers (who uses PublicWorks and what)\n")
    print("| File | Component | What is used |")
    print("|------|-----------|--------------|")
    for file, comp, what in trace_callers():
        print(f"| {file} | {comp} | {what} |")
    print("\n## Open questions (for manual probe)\n")
    print("- Which adapters are actually **created** at boot? (Config may omit redis/consul/kreuzberg → adapter not created.)")
    print("- Which abstractions are **invoked** on first request vs never?")
    print("- Is the 5-layer flow **always** adapter→abstraction→protocol, or do some callers bypass?")
    print("\n---\n*Probe 04 complete. Copy above into Public Works Reality Map; run manual traces for 'actually created' and 'actually used'.*")


if __name__ == "__main__":
    main()
