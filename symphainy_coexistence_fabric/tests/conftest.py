"""
Root test conftest – shared fixtures for all test trees.

E2E demo paths (tests/e2e/demo_paths/) need the same solution and execution_context
fixtures as 3d tests. This module loads tests/3d/conftest.py and re-exports those
fixtures so pytest discovers them when running tests/e2e/ (3d directory name is not
a valid Python module, so we cannot use pytest_plugins = ["tests.3d.conftest"]).

Contract: E2E and 3d share fixture definitions from tests/3d/conftest.py.
See docs/testing/stability_gravity_reports/20260129_e2e_fixture_scope.md.
"""

import sys
import importlib.util
from pathlib import Path

_project_root = Path(__file__).resolve().parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Load tests/3d/conftest.py so e2e tests get the same fixtures
_conftest_3d_path = Path(__file__).resolve().parent / "3d" / "conftest.py"
_spec = importlib.util.spec_from_file_location("conftest_3d", _conftest_3d_path)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["conftest_3d"] = _mod
_spec.loader.exec_module(_mod)

# Re-export fixtures so pytest discovers them when running tests/e2e/
mock_public_works = _mod.mock_public_works
mock_state_surface = _mod.mock_state_surface
mock_solution_registry = _mod.mock_solution_registry
mock_intent_registry = _mod.mock_intent_registry
mock_curator = _mod.mock_curator
execution_context = _mod.execution_context
coexistence_solution = _mod.coexistence_solution
content_solution = _mod.content_solution
insights_solution = _mod.insights_solution
operations_solution = _mod.operations_solution
outcomes_solution = _mod.outcomes_solution
security_solution = _mod.security_solution
control_tower = _mod.control_tower
