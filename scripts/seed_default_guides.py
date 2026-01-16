"""
Seed Default Guides - Create Default Guides for Common Use Cases

Script to seed default guides (PSO, AAR, Variable Whole Life Insurance Policy, etc.) into Supabase.

Usage:
    python3 scripts/seed_default_guides.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
from symphainy_platform.foundations.public_works.adapters.supabase_adapter import SupabaseAdapter
from symphainy_platform.civic_systems.platform_sdk.guide_registry import GuideRegistry
from utilities import get_logger

logger = get_logger("SeedDefaultGuides")


# Default Guides
DEFAULT_GUIDES = {
    "pso_permit_guide": {
        "guide_id": "pso_permit_guide",
        "name": "PSO Permit Guide",
        "description": "Default guide for Permits (PSO) analysis",
        "type": "default",
        "fact_pattern": {
            "entities": [
                {
                    "entity_type": "permit",
                    "attributes": {
                        "permit_id": "string",
                        "permit_type": "string",
                        "status": "string",
                        "issue_date": "date",
                        "expiry_date": "date"
                    }
                },
                {
                    "entity_type": "applicant",
                    "attributes": {
                        "applicant_name": "string",
                        "applicant_id": "string",
                        "contact_info": "string"
                    }
                },
                {
                    "entity_type": "property",
                    "attributes": {
                        "property_address": "string",
                        "property_id": "string",
                        "property_type": "string"
                    }
                },
                {
                    "entity_type": "regulation",
                    "attributes": {
                        "regulation_code": "string",
                        "regulation_name": "string",
                        "compliance_status": "string"
                    }
                }
            ],
            "relationships": [
                {
                    "from": "permit",
                    "to": "applicant",
                    "type": "owned_by"
                },
                {
                    "from": "permit",
                    "to": "property",
                    "type": "applies_to"
                },
                {
                    "from": "permit",
                    "to": "regulation",
                    "type": "governed_by"
                }
            ]
        },
        "output_template": {
            "version": "1.0",
            "structure": {
                "permit_summary": {
                    "permit_id": "{{permit.permit_id}}",
                    "status": "{{permit.status}}",
                    "applicant": "{{applicant.applicant_name}}",
                    "property": "{{property.property_address}}"
                },
                "compliance": {
                    "regulation": "{{regulation.regulation_name}}",
                    "status": "{{regulation.compliance_status}}"
                }
            }
        }
    },
    "aar_report_guide": {
        "guide_id": "aar_report_guide",
        "name": "AAR (After Action Report) Guide",
        "description": "Default guide for After Action Reports (AAR) analysis",
        "type": "default",
        "fact_pattern": {
            "entities": [
                {
                    "entity_type": "event",
                    "attributes": {
                        "event_id": "string",
                        "event_name": "string",
                        "event_date": "date",
                        "event_type": "string"
                    }
                },
                {
                    "entity_type": "action",
                    "attributes": {
                        "action_id": "string",
                        "action_description": "string",
                        "action_taken_by": "string",
                        "action_timestamp": "datetime"
                    }
                },
                {
                    "entity_type": "outcome",
                    "attributes": {
                        "outcome_id": "string",
                        "outcome_description": "string",
                        "outcome_status": "string",
                        "outcome_impact": "string"
                    }
                },
                {
                    "entity_type": "lesson_learned",
                    "attributes": {
                        "lesson_id": "string",
                        "lesson_description": "string",
                        "lesson_category": "string",
                        "recommendation": "string"
                    }
                }
            ],
            "relationships": [
                {
                    "from": "event",
                    "to": "action",
                    "type": "triggered"
                },
                {
                    "from": "action",
                    "to": "outcome",
                    "type": "resulted_in"
                },
                {
                    "from": "outcome",
                    "to": "lesson_learned",
                    "type": "generated"
                }
            ]
        },
        "output_template": {
            "version": "1.0",
            "structure": {
                "aar_summary": {
                    "event": "{{event.event_name}}",
                    "date": "{{event.event_date}}",
                    "actions_taken": "{{action.action_description}}",
                    "outcomes": "{{outcome.outcome_description}}",
                    "lessons_learned": "{{lesson_learned.lesson_description}}"
                }
            }
        }
    },
    "variable_whole_life_policy_guide": {
        "guide_id": "variable_whole_life_policy_guide",
        "name": "Variable Whole Life Insurance Policy Record for Migration",
        "description": "Default guide for Variable Whole Life Insurance Policy Record analysis and migration",
        "type": "default",
        "fact_pattern": {
            "entities": [
                {
                    "entity_type": "policy",
                    "attributes": {
                        "policy_number": "string",
                        "policy_type": "string",
                        "issue_date": "date",
                        "status": "string",
                        "face_amount": "decimal",
                        "cash_value": "decimal",
                        "death_benefit": "decimal",
                        "premium_amount": "decimal",
                        "premium_frequency": "string"
                    }
                },
                {
                    "entity_type": "policyholder",
                    "attributes": {
                        "policyholder_id": "string",
                        "policyholder_name": "string",
                        "date_of_birth": "date",
                        "gender": "string",
                        "contact_info": "string",
                        "address": "string"
                    }
                },
                {
                    "entity_type": "beneficiary",
                    "attributes": {
                        "beneficiary_id": "string",
                        "beneficiary_name": "string",
                        "relationship": "string",
                        "percentage": "decimal",
                        "beneficiary_type": "string"
                    }
                },
                {
                    "entity_type": "coverage",
                    "attributes": {
                        "coverage_type": "string",
                        "coverage_amount": "decimal",
                        "riders": "array",
                        "exclusions": "array"
                    }
                },
                {
                    "entity_type": "premium",
                    "attributes": {
                        "premium_id": "string",
                        "premium_amount": "decimal",
                        "premium_frequency": "string",
                        "payment_method": "string",
                        "next_due_date": "date"
                    }
                },
                {
                    "entity_type": "migration_info",
                    "attributes": {
                        "source_system": "string",
                        "migration_date": "date",
                        "migration_status": "string",
                        "source_policy_id": "string",
                        "migration_notes": "string"
                    }
                }
            ],
            "relationships": [
                {
                    "from": "policy",
                    "to": "policyholder",
                    "type": "owned_by"
                },
                {
                    "from": "policy",
                    "to": "beneficiary",
                    "type": "benefits"
                },
                {
                    "from": "policy",
                    "to": "coverage",
                    "type": "provides"
                },
                {
                    "from": "policy",
                    "to": "premium",
                    "type": "requires"
                },
                {
                    "from": "policy",
                    "to": "migration_info",
                    "type": "migrated_from"
                }
            ]
        },
        "output_template": {
            "version": "1.0",
            "structure": {
                "policy_summary": {
                    "policy_number": "{{policy.policy_number}}",
                    "policy_type": "{{policy.policy_type}}",
                    "status": "{{policy.status}}",
                    "face_amount": "{{policy.face_amount}}",
                    "issue_date": "{{policy.issue_date}}"
                },
                "policyholder_info": {
                    "name": "{{policyholder.policyholder_name}}",
                    "date_of_birth": "{{policyholder.date_of_birth}}",
                    "contact": "{{policyholder.contact_info}}"
                },
                "beneficiaries": {
                    "primary": "{{beneficiary.beneficiary_name}}",
                    "relationship": "{{beneficiary.relationship}}",
                    "percentage": "{{beneficiary.percentage}}"
                },
                "coverage_details": {
                    "coverage_type": "{{coverage.coverage_type}}",
                    "coverage_amount": "{{coverage.coverage_amount}}",
                    "riders": "{{coverage.riders}}"
                },
                "premium_info": {
                    "amount": "{{premium.premium_amount}}",
                    "frequency": "{{premium.premium_frequency}}",
                    "next_due_date": "{{premium.next_due_date}}"
                },
                "migration_info": {
                    "source_system": "{{migration_info.source_system}}",
                    "migration_date": "{{migration_info.migration_date}}",
                    "migration_status": "{{migration_info.migration_status}}",
                    "source_policy_id": "{{migration_info.source_policy_id}}"
                }
            }
        }
    }
}


async def seed_default_guides():
    """Seed default guides into Supabase."""
    # Get Supabase configuration from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_service_key:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        return False
    
    # Initialize Supabase adapter
    supabase_adapter = SupabaseAdapter(
        url=supabase_url,
        anon_key="",  # Not needed for service key operations
        service_key=supabase_service_key
    )
    
    # Initialize Guide Registry
    guide_registry = GuideRegistry(supabase_adapter=supabase_adapter)
    
    # Use a system tenant ID for default guides (or create a special tenant)
    system_tenant_id = "00000000-0000-0000-0000-000000000000"  # System tenant
    
    logger.info("Seeding default guides...")
    
    success_count = 0
    for guide_key, guide_data in DEFAULT_GUIDES.items():
        try:
            result = await guide_registry.register_guide(
                guide_id=guide_data["guide_id"],
                guide=guide_data,
                tenant_id=system_tenant_id
            )
            
            if result:
                logger.info(f"✅ Seeded guide: {guide_data['name']}")
                success_count += 1
            else:
                logger.warning(f"⚠️ Failed to seed guide: {guide_data['name']}")
        except Exception as e:
            logger.error(f"❌ Error seeding guide {guide_data['name']}: {e}", exc_info=True)
    
    logger.info(f"Seeded {success_count}/{len(DEFAULT_GUIDES)} default guides")
    return success_count == len(DEFAULT_GUIDES)


if __name__ == "__main__":
    asyncio.run(seed_default_guides())
