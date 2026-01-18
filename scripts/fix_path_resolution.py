#!/usr/bin/env python3
"""
Fix path resolution issues in all Python files.

Replaces hardcoded .parents[N] with dynamic project root detection.
"""
import re
from pathlib import Path

# Pattern to match
pattern = re.compile(
    r'project_root\s*=\s*Path\(__file__\)\.resolve\(\)\.parents\[\d+\]'
)

# Replacement code
replacement = '''# Find project root by looking for common markers (pyproject.toml, requirements.txt, etc.)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent'''

# Files to fix
files_to_fix = [
    "symphainy_platform/civic_systems/agentic/agents/guide_agent.py",
    "symphainy_platform/civic_systems/agentic/agents/workflow_optimization_agent.py",
    "symphainy_platform/civic_systems/agentic/agents/proposal_agent.py",
    "symphainy_platform/civic_systems/agentic/agents/eda_analysis_agent.py",
    "symphainy_platform/civic_systems/agentic/agents/insights_eda_agent.py",
    "symphainy_platform/civic_systems/agentic/agents/roadmap_proposal_agent.py",
    "symphainy_platform/civic_systems/agentic/agents/content_liaison_agent.py",
    "symphainy_platform/civic_systems/agentic/agents/workflow_optimization_specialist.py",
    "symphainy_platform/civic_systems/agentic/agents/conversational_agent.py",
]

project_root = Path(__file__).parent

for file_path in files_to_fix:
    full_path = project_root / file_path
    if not full_path.exists():
        print(f"⚠️  File not found: {file_path}")
        continue
    
    content = full_path.read_text()
    
    # Check if it needs fixing
    if pattern.search(content):
        # Replace the pattern
        new_content = pattern.sub(replacement, content)
        full_path.write_text(new_content)
        print(f"✅ Fixed: {file_path}")
    else:
        print(f"⏭️  Already fixed or no match: {file_path}")

print("\n✅ Path resolution fixes complete!")
