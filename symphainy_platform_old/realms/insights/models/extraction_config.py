"""
Extraction Config Models - JSON Schema-Based Configuration

Data models for structured extraction configurations.
Uses JSON Schema for validation and flexibility.

WHAT (Model Role): I define extraction configuration structure
HOW (Model Implementation): I use JSON Schema for validation and Python dataclasses for runtime
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
import json


# JSON Schema for ExtractionConfig validation
EXTRACTION_CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "config_id": {
            "type": "string",
            "description": "Unique identifier for extraction config"
        },
        "name": {
            "type": "string",
            "description": "User-facing name"
        },
        "description": {
            "type": "string",
            "description": "User-facing description"
        },
        "domain": {
            "type": "string",
            "enum": ["variable_life_policy_rules", "aar", "pso", "custom"],
            "description": "Domain/pattern type"
        },
        "categories": {
            "type": "array",
            "items": {
                "$ref": "#/definitions/ExtractionCategory"
            },
            "description": "List of extraction categories",
            "minItems": 1
        },
        "extraction_order": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Order in which categories should be extracted"
        },
        "dependencies": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {"type": "string"}
            },
            "description": "Category dependencies (category_name -> [depends_on_categories])"
        },
        "output_schema": {
            "type": "object",
            "description": "JSON Schema for output validation",
            "additionalProperties": True
        },
        "custom_properties": {
            "type": "object",
            "description": "Domain-specific customizations (flexible schema)",
            "additionalProperties": True
        },
        "version": {
            "type": "string",
            "default": "1.0"
        },
        "created_by": {
            "type": ["string", "null"]
        }
    },
    "required": ["config_id", "name", "domain", "categories"],
    "definitions": {
        "ExtractionCategory": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Category name"
                },
                "description": {
                    "type": "string",
                    "description": "Category description"
                },
                "extraction_type": {
                    "type": "string",
                    "enum": ["llm", "pattern", "embedding", "hybrid"],
                    "description": "Extraction method"
                },
                "prompt_template": {
                    "type": "string",
                    "description": "Prompt template for LLM-based extraction"
                },
                "validation_rules": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": True
                    },
                    "description": "Validation rules for extracted data"
                },
                "required": {
                    "type": "boolean",
                    "default": False
                },
                "custom_properties": {
                    "type": "object",
                    "additionalProperties": True,
                    "description": "Category-specific customizations"
                }
            },
            "required": ["name", "extraction_type"]
        }
    }
}


@dataclass
class ExtractionCategory:
    """
    Extraction Category - Defines what to extract and how.
    """
    name: str
    extraction_type: str  # "llm", "pattern", "embedding", "hybrid"
    description: str = ""
    prompt_template: str = ""
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    required: bool = False
    custom_properties: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        # Remove None values for JSON serialization
        if result.get("custom_properties") is None:
            result.pop("custom_properties", None)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractionCategory":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            extraction_type=data["extraction_type"],
            description=data.get("description", ""),
            prompt_template=data.get("prompt_template", ""),
            validation_rules=data.get("validation_rules", []),
            required=data.get("required", False),
            custom_properties=data.get("custom_properties")
        )


@dataclass
class ExtractionConfig:
    """
    Extraction Config - Complete configuration for structured extraction.
    """
    config_id: str
    name: str
    domain: str
    categories: List[ExtractionCategory]
    description: str = ""
    extraction_order: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    custom_properties: Optional[Dict[str, Any]] = None
    version: str = "1.0"
    created_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (JSON Schema compliant)."""
        result = {
            "config_id": self.config_id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "categories": [cat.to_dict() for cat in self.categories],
            "extraction_order": self.extraction_order,
            "dependencies": self.dependencies,
            "output_schema": self.output_schema,
            "version": self.version
        }
        
        if self.custom_properties:
            result["custom_properties"] = self.custom_properties
        if self.created_by:
            result["created_by"] = self.created_by
        
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractionConfig":
        """Create from dictionary."""
        categories = [
            ExtractionCategory.from_dict(cat_data)
            for cat_data in data.get("categories", [])
        ]
        
        return cls(
            config_id=data["config_id"],
            name=data["name"],
            description=data.get("description", ""),
            domain=data["domain"],
            categories=categories,
            extraction_order=data.get("extraction_order", []),
            dependencies=data.get("dependencies", {}),
            output_schema=data.get("output_schema", {}),
            custom_properties=data.get("custom_properties"),
            version=data.get("version", "1.0"),
            created_by=data.get("created_by")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "ExtractionConfig":
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate config against JSON Schema.
        
        Returns:
            (is_valid, error_message)
        """
        try:
            import jsonschema
            jsonschema.validate(self.to_dict(), EXTRACTION_CONFIG_SCHEMA)
            return True, None
        except ImportError:
            return False, "jsonschema library not installed"
        except jsonschema.ValidationError as e:
            return False, f"Validation error: {e.message}"
        except Exception as e:
            return False, f"Validation failed: {str(e)}"
