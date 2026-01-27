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
# Script can be run from:
# 1. symphainy_platform/scripts/seed_default_guides.py -> go up 2 levels
# 2. scripts/seed_default_guides.py -> go up 1 level
# 3. symphainy_platform/ -> go up 1 level
script_path = Path(__file__).resolve()
if script_path.parts[-3:-1] == ('symphainy_platform', 'scripts'):
    # Running from symphainy_platform/scripts/
    project_root = script_path.parents[2]
elif script_path.parts[-2] == 'scripts':
    # Running from scripts/
    project_root = script_path.parents[1]
else:
    # Running from symphainy_platform/ or elsewhere
    project_root = script_path.parents[1]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
from symphainy_platform.foundations.public_works.adapters.supabase_adapter import SupabaseAdapter
from symphainy_platform.civic_systems.platform_sdk.guide_registry import GuideRegistry
from symphainy_platform.config.config_helper import _find_env_secrets, load_env_file
from utilities import get_logger

logger = get_logger("SeedDefaultGuides")

# Load .env.secrets automatically if available
env_secrets_path = _find_env_secrets()
if env_secrets_path:
    logger.info(f"Loading environment variables from: {env_secrets_path}")
    env_vars = load_env_file(str(env_secrets_path))
    for key, value in env_vars.items():
        if key not in os.environ:  # Don't override existing env vars
            os.environ[key] = value
    logger.info(f"✅ Loaded {len(env_vars)} environment variables from .env.secrets")
else:
    logger.warning("⚠️ No .env.secrets file found. Using environment variables only.")


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
    # Get Supabase configuration from environment (already loaded from .env.secrets if available)
    # Use correct variable names from .env.secrets:
    # - SUPABASE_URL
    # - SUPABASE_SECRET_KEY (preferred) or SUPABASE_SERVICE_KEY (fallback)
    supabase_url = os.getenv("SUPABASE_URL")
    
    # Try SUPABASE_SECRET_KEY first (preferred), then SUPABASE_SERVICE_KEY (fallback)
    supabase_secret_key = (
        os.getenv("SUPABASE_SECRET_KEY") or
        os.getenv("SUPABASE_SERVICE_KEY")
    )
    
    if not supabase_url:
        logger.error("SUPABASE_URL must be set (via environment variable or .env.secrets)")
        logger.error("   Expected location: symphainy_platform/.env.secrets or project root/.env.secrets")
        logger.error("   Available variables: SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, SUPABASE_SECRET_KEY")
        return False
    
    if not supabase_secret_key:
        logger.error("SUPABASE_SECRET_KEY (or SUPABASE_SERVICE_KEY) must be set (via environment variable or .env.secrets)")
        logger.error("   Expected location: symphainy_platform/.env.secrets or project root/.env.secrets")
        logger.error("   Note: SUPABASE_SECRET_KEY is the service key for admin operations")
        logger.error("   Fallback: SUPABASE_SERVICE_KEY is also supported for backward compatibility")
        return False
    
    logger.info(f"Using Supabase URL: {supabase_url[:30]}..." if len(supabase_url) > 30 else f"Using Supabase URL: {supabase_url}")
    
    # Log which key was used
    if os.getenv("SUPABASE_SECRET_KEY"):
        logger.info("Using SUPABASE_SECRET_KEY for admin operations")
    elif os.getenv("SUPABASE_SERVICE_KEY"):
        logger.info("Using SUPABASE_SERVICE_KEY for admin operations (legacy variable name)")
    
    # Get publishable key for anon_client (SupabaseAdapter requires it even when using service key)
    supabase_publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not supabase_publishable_key:
        logger.warning("⚠️ SUPABASE_PUBLISHABLE_KEY not found. Using SUPABASE_SECRET_KEY for both clients.")
        logger.warning("   This works but SUPABASE_PUBLISHABLE_KEY is recommended for anon_client.")
        supabase_publishable_key = supabase_secret_key  # Fallback to secret key
    
    # Initialize Supabase adapter
    # Use SUPABASE_SECRET_KEY (service key) for admin operations like seeding
    # anon_key is required by SupabaseAdapter even when using service key
    supabase_adapter = SupabaseAdapter(
        url=supabase_url,
        anon_key=supabase_publishable_key,  # Required by SupabaseAdapter, even if using service key
        service_key=supabase_secret_key
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
