"""
Civic System Composition - Compose Civic Systems

Provides utilities for composing Smart City, Experience, and Agentic systems.

WHAT (Platform SDK Role): I provide composition utilities for Civic Systems
HOW (Platform SDK Implementation): I compose Smart City + Experience + Agentic
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger

from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK
from symphainy_platform.civic_systems.experience.sdk.runtime_client import RuntimeClient
from symphainy_platform.civic_systems.agentic.agent_registry import AgentRegistry


class CivicComposition:
    """
    Composition utilities for Civic Systems.
    
    Provides pre-configured compositions of Smart City, Experience, and Agentic systems.
    """
    
    def __init__(
        self,
        smart_city_sdk: Optional[TrafficCopSDK] = None,
        experience_client: Optional[RuntimeClient] = None,
        agent_registry: Optional[AgentRegistry] = None
    ):
        """
        Initialize civic composition.
        
        Args:
            smart_city_sdk: Optional Smart City SDK (Traffic Cop)
            experience_client: Optional Experience client (Runtime client)
            agent_registry: Optional Agent registry
        """
        self.smart_city_sdk = smart_city_sdk
        self.experience_client = experience_client
        self.agent_registry = agent_registry
        self.logger = get_logger(self.__class__.__name__)
    
    @staticmethod
    def compose_smart_city_experience(
        smart_city_sdk: TrafficCopSDK,
        experience_client: RuntimeClient
    ) -> Dict[str, Any]:
        """
        Compose Smart City + Experience systems.
        
        Provides governance + user experience.
        
        Args:
            smart_city_sdk: Smart City SDK
            experience_client: Experience client
        
        Returns:
            Composition configuration
        """
        return {
            "composition_type": "smart_city_experience",
            "components": {
                "smart_city": {
                    "sdk": smart_city_sdk,
                    "capabilities": ["session_validation", "rate_limiting", "policy_enforcement"]
                },
                "experience": {
                    "client": experience_client,
                    "capabilities": ["intent_submission", "execution_streaming", "session_management"]
                }
            },
            "integration_points": [
                "session_validation",
                "intent_submission",
                "execution_streaming"
            ]
        }
    
    @staticmethod
    def compose_smart_city_agentic(
        smart_city_sdk: TrafficCopSDK,
        agent_registry: AgentRegistry
    ) -> Dict[str, Any]:
        """
        Compose Smart City + Agentic systems.
        
        Provides governance + agent collaboration.
        
        Args:
            smart_city_sdk: Smart City SDK
            agent_registry: Agent registry
        
        Returns:
            Composition configuration
        """
        return {
            "composition_type": "smart_city_agentic",
            "components": {
                "smart_city": {
                    "sdk": smart_city_sdk,
                    "capabilities": ["collaboration_validation", "policy_enforcement"]
                },
                "agentic": {
                    "registry": agent_registry,
                    "capabilities": ["agent_collaboration", "contribution_requests"]
                }
            },
            "integration_points": [
                "collaboration_validation",
                "policy_enforcement"
            ]
        }
    
    @staticmethod
    def compose_experience_agentic(
        experience_client: RuntimeClient,
        agent_registry: AgentRegistry
    ) -> Dict[str, Any]:
        """
        Compose Experience + Agentic systems.
        
        Provides user experience + agent collaboration.
        
        Args:
            experience_client: Experience client
            agent_registry: Agent registry
        
        Returns:
            Composition configuration
        """
        return {
            "composition_type": "experience_agentic",
            "components": {
                "experience": {
                    "client": experience_client,
                    "capabilities": ["intent_submission", "execution_streaming"]
                },
                "agentic": {
                    "registry": agent_registry,
                    "capabilities": ["agent_collaboration", "contribution_requests"]
                }
            },
            "integration_points": [
                "intent_submission",
                "execution_streaming"
            ]
        }
    
    @staticmethod
    def compose_all(
        smart_city_sdk: TrafficCopSDK,
        experience_client: RuntimeClient,
        agent_registry: AgentRegistry
    ) -> Dict[str, Any]:
        """
        Compose all three Civic Systems.
        
        Provides full platform capabilities: governance + experience + agentic.
        
        Args:
            smart_city_sdk: Smart City SDK
            experience_client: Experience client
            agent_registry: Agent registry
        
        Returns:
            Full composition configuration
        """
        return {
            "composition_type": "full_platform",
            "components": {
                "smart_city": {
                    "sdk": smart_city_sdk,
                    "capabilities": [
                        "session_validation",
                        "rate_limiting",
                        "policy_enforcement",
                        "collaboration_validation"
                    ]
                },
                "experience": {
                    "client": experience_client,
                    "capabilities": [
                        "intent_submission",
                        "execution_streaming",
                        "session_management"
                    ]
                },
                "agentic": {
                    "registry": agent_registry,
                    "capabilities": [
                        "agent_collaboration",
                        "contribution_requests",
                        "tool_usage"
                    ]
                }
            },
            "integration_points": [
                "session_validation",
                "intent_submission",
                "execution_streaming",
                "collaboration_validation",
                "policy_enforcement"
            ]
        }
    
    def validate_composition(self, composition: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate composition configuration.
        
        Args:
            composition: Composition configuration
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        if "composition_type" not in composition:
            return False, "composition_type is required"
        
        if "components" not in composition:
            return False, "components is required"
        
        # Validate components based on composition type
        composition_type = composition["composition_type"]
        components = composition["components"]
        
        if composition_type == "smart_city_experience":
            if "smart_city" not in components or "experience" not in components:
                return False, "smart_city_experience requires smart_city and experience components"
        
        elif composition_type == "smart_city_agentic":
            if "smart_city" not in components or "agentic" not in components:
                return False, "smart_city_agentic requires smart_city and agentic components"
        
        elif composition_type == "experience_agentic":
            if "experience" not in components or "agentic" not in components:
                return False, "experience_agentic requires experience and agentic components"
        
        elif composition_type == "full_platform":
            if "smart_city" not in components or "experience" not in components or "agentic" not in components:
                return False, "full_platform requires smart_city, experience, and agentic components"
        
        else:
            return False, f"Unknown composition type: {composition_type}"
        
        return True, None
