"""
Smart City - Phase 4

Smart City is BOTH:
- Plane: Governance/Control Plane (observes Runtime, enforces policy)
- Realm: Platform Realm (special realm that's always present)

Provides:
- Smart City services (Security Guard, Traffic Cop, Post Office, etc.)
- Governance and policy enforcement
- Observability and telemetry
- Platform infrastructure capabilities
"""

from .foundation_service import SmartCityFoundationService
from .protocols.smart_city_service_protocol import SmartCityServiceProtocol

__all__ = [
    "SmartCityFoundationService",
    "SmartCityServiceProtocol",
]
