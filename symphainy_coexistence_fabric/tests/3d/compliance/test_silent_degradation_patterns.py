"""
Contract test: find hidden "silent degradation" patterns in platform code.

Aligns with PLATFORM_CONTRACT.md §8A (No Silent Degradation at Runtime) and
TESTING_STRATEGY_PLATFORM_CONTRACT.md §4 item 4 and §6 (static checks).

Scans symphainy_platform for patterns that violate the contract:
- "if not self.<dep>:" followed by return of a default (False, None, [], {}, 0, etc.)
  instead of raising
- "if not self.<dep>:" followed by fallback / in-memory behavior instead of raising

These patterns hide missing required dependencies and make failures hard to diagnose.
The test FAILS when any violation is found and reports file:line and snippet.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


# Root of the repo (tests/3d/compliance -> repo root)
REPO_ROOT = Path(__file__).resolve().parents[3]
PLATFORM_ROOT = REPO_ROOT / "symphainy_platform"

# Patterns that indicate silent degradation (forbidden when guarding a required dep)
DEFAULT_RETURN_PATTERN = re.compile(
    r"\breturn\s+(\[\s*\]|\{\s*\}|False|None|0\b|\"\"|''|set\s*\(\s*\))\s*(#|$)"
)
FALLBACK_PATTERN = re.compile(
    r"fallback|in-memory\s+fallback|using\s+in-memory",
    re.IGNORECASE,
)
# Compliant: raise in the same block
RAISE_PATTERN = re.compile(r"\braise\s+")

# "if not self.<name>:" at start of line (after optional whitespace)
IF_NOT_SELF_PATTERN = re.compile(r"^\s*if\s+not\s+self\.(\w+)\s*:")


def _block_lines(lines: list[str], start_index: int) -> list[tuple[int, str]]:
    """Return (line_number_1based, line) for the block body after the if at start_index."""
    if start_index >= len(lines):
        return []
    if_line = lines[start_index]
    base_indent = len(if_line) - len(if_line.lstrip())
    result = []
    for i in range(start_index + 1, len(lines)):
        line = lines[i]
        if not line.strip():
            result.append((i + 1, line))
            continue
        line_indent = len(line) - len(line.lstrip())
        if line_indent <= base_indent:
            break
        result.append((i + 1, line))
    return result


def _is_default_return(line: str) -> bool:
    """True if line is a return of a default value (empty list/dict, False, None, 0)."""
    stripped = line.strip()
    if not stripped.startswith("return "):
        return False
    return bool(DEFAULT_RETURN_PATTERN.search(line))


def _is_fallback_comment_or_behavior(line: str) -> bool:
    """True if line suggests fallback / in-memory behavior (comment or code)."""
    if not FALLBACK_PATTERN.search(line):
        return False
    # Exclude "no fallback" / "required - no fallback" (contract-compliant comments)
    if re.search(r"no\s+fallback|required\s*[-—]\s*no\s+fallback", line, re.IGNORECASE):
        return False
    return True


def _is_raise(line: str) -> bool:
    """True if line contains a raise statement (same block response to missing dep)."""
    return bool(RAISE_PATTERN.search(line))


def scan_file(file_path: Path) -> list[dict]:
    """
    Scan a single Python file for silent-degradation patterns.

    Returns list of violations: [{"line": N, "snippet": str, "reason": str}, ...]
    """
    violations = []
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [{"line": 0, "snippet": str(e), "reason": "read_error"}]
    lines = text.splitlines()

    for i, line in enumerate(lines):
        m = IF_NOT_SELF_PATTERN.search(line)
        if not m:
            continue
        dep_name = m.group(1)
        block = _block_lines(lines, i)
        if not block:
            continue

        # In the block, find first occurrence of: raise, default return, or fallback
        first_raise_line = None
        first_return_or_fallback_line = None
        first_return_or_fallback_reason = None

        for ln, content in block:
            if _is_raise(content):
                if first_raise_line is None:
                    first_raise_line = ln
            if first_return_or_fallback_line is None:
                if _is_default_return(content):
                    first_return_or_fallback_line = ln
                    first_return_or_fallback_reason = "return default (silent degradation)"
                elif _is_fallback_comment_or_behavior(content):
                    first_return_or_fallback_line = ln
                    first_return_or_fallback_reason = "fallback / in-memory (silent degradation)"

        # Violation if we have return/fallback and either no raise or return/fallback before raise
        if first_return_or_fallback_line is None:
            continue
        if first_raise_line is not None and first_raise_line < first_return_or_fallback_line:
            # Raise comes first in block -> compliant
            continue

        snippet = "\n".join(
            content for _, content in block[:8]
        ).strip() or line.strip()
        violations.append({
            "line": first_return_or_fallback_line,
            "if_line": i + 1,
            "dep": dep_name,
            "snippet": snippet[:400],
            "reason": first_return_or_fallback_reason,
        })
    return violations


def collect_platform_py_files() -> list[Path]:
    """All .py files under symphainy_platform, excluding __pycache__ and adapters.

    §8A applies to platform components (services, registries, SDKs, backends,
    abstractions). Infrastructure adapters (public_works/adapters/) are excluded:
    they report \"not connected\" via return values; startup/health checks ensure
    they are connected before use.
    """
    if not PLATFORM_ROOT.is_dir():
        return []
    files = []
    for path in PLATFORM_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        if "public_works" in path.parts and "adapters" in path.parts:
            continue
        files.append(path)
    return sorted(files)


@pytest.mark.contract
def test_no_silent_degradation_patterns_in_platform():
    """
    Contract test: no 'if not self.<dep>: return default' or fallback patterns.

    Scans symphainy_platform for violations of PLATFORM_CONTRACT §8A.
    Fails with a clear report of file:line and snippet for each violation.
    """
    files = collect_platform_py_files()
    all_violations = []
    for path in files:
        rel = path.relative_to(REPO_ROOT)
        for v in scan_file(path):
            all_violations.append({
                "file": str(rel),
                "if_line": v["if_line"],
                "line": v["line"],
                "dep": v["dep"],
                "reason": v["reason"],
                "snippet": v["snippet"],
            })

    if not all_violations:
        return

    # Build report
    lines_report = []
    lines_report.append(
        "Platform contract §8A violation: silent degradation patterns found. "
        "Required dependencies must not be guarded by 'return default' or 'fallback'; "
        "they must raise. See PLATFORM_CONTRACT.md §8A and TESTING_STRATEGY_PLATFORM_CONTRACT.md."
    )
    for v in all_violations:
        lines_report.append(
            f"  {v['file']}:{v['line']} (if at {v['if_line']}) — {v['dep']!r}: {v['reason']}"
        )
        lines_report.append(f"    snippet: {v['snippet'][:200].replace(chr(10), ' ')}...")
    msg = "\n".join(lines_report)
    raise AssertionError(msg)
