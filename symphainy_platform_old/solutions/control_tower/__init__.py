"""
Control Tower - Platform Command Center

The Control Tower is the nerve center of the Symphainy Platform, providing:
- Platform Monitoring: Real-time observability into platform health and execution
- Solution Management: Lifecycle management for deployed solutions
- Developer Experience: Documentation, patterns, and playground access
- Solution Composition: Guided creation of new solutions from templates

WHAT (Control Tower Role): I am the platform's command center
HOW (Control Tower Implementation): I compose monitoring, management, and composition journeys

Note: Control Tower was previously known as "Admin Dashboard" - this is the sexier name.
"""

from .control_tower import ControlTower

__all__ = ["ControlTower"]
