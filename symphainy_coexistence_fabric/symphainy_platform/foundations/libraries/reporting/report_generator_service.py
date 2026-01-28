"""
Report Generator Service - Pure Data Processing for Report Generation

Enabling service for generating reports and summaries.

WHAT (Enabling Service Role): I execute report generation
HOW (Enabling Service Implementation): I use Public Works abstractions for report generation

Key Principle: Pure data processing - no LLM, no business logic, no orchestration.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from datetime import datetime

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext


class ReportGeneratorService:
    """
    Report Generator Service - Pure data processing for report generation.
    
    Uses Public Works abstractions to generate reports and summaries.
    Returns raw data only - no business logic.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Report Generator Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
    
    async def generate_pillar_summary(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate pillar summary report from all pillar outputs.
        
        Args:
            content_summary: Content pillar summary
            insights_summary: Insights pillar summary
            journey_summary: Journey pillar summary
            tenant_id: Tenant ID
            context: Execution context
        
        Returns:
            Dict with summary report data
        """
        # Generate summary visualization
        summary = {
            "content_pillar": {
                "status": "completed" if content_summary else "pending",
                "files_uploaded": content_summary.get("files_uploaded", 0) if content_summary else 0,
                "files_parsed": content_summary.get("files_parsed", 0) if content_summary else 0,
                "embeddings_generated": content_summary.get("embeddings_generated", 0) if content_summary else 0
            },
            "insights_pillar": {
                "status": "completed" if insights_summary else "pending",
                "insights_generated": insights_summary.get("insights_count", 0) if insights_summary else 0,
                "metrics_calculated": insights_summary.get("metrics_count", 0) if insights_summary else 0,
                "relationships_mapped": insights_summary.get("relationships_count", 0) if insights_summary else 0
            },
            "journey_pillar": {
                "status": "completed" if journey_summary else "pending",
                "workflows_created": journey_summary.get("workflows_created", 0) if journey_summary else 0,
                "sops_generated": journey_summary.get("sops_generated", 0) if journey_summary else 0,
                "blueprints_created": journey_summary.get("blueprints_created", 0) if journey_summary else 0
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return summary
    
    async def generate_realm_summary_visuals(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate realm-specific summary visuals for each pillar.
        
        ARCHITECTURAL PRINCIPLE: Creates visual summaries for each realm's outputs.
        Uses Public Works abstractions to gather real data from realms.
        
        Args:
            content_summary: Content pillar summary
            insights_summary: Insights pillar summary
            journey_summary: Journey pillar summary
            tenant_id: Tenant ID
            context: Execution context
        
        Returns:
            Dict with realm-specific visual data (tutorial format for Content, ecosystem for Insights, friction removal for Journey)
        """
        self.logger.info("Generating realm-specific summary visuals with real data")
        
        # Gather real data from realms via Public Works abstractions
        content_visual = await self._generate_content_visual(
            content_summary, tenant_id, context
        )
        
        insights_visual = await self._generate_insights_visual(
            insights_summary, tenant_id, context
        )
        
        journey_visual = await self._generate_journey_visual(
            journey_summary, tenant_id, context
        )
        
        return {
            "content_visual": content_visual,
            "insights_visual": insights_visual,
            "journey_visual": journey_visual,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_content_visual(
        self,
        content_summary: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate Content pillar visual - Data Mash Tutorial.
        
        Gathers real data from Content realm via Public Works abstractions.
        """
        # Gather real data from FileStorageAbstraction
        files_uploaded = 0
        files_parsed = 0
        deterministic_embeddings_count = 0
        semantic_embeddings_count = 0
        target_models_count = 0
        
        file_examples = []
        parsed_examples = []
        embedding_examples = []
        
        try:
            if self.public_works:
                file_storage = self.public_works.get_file_storage_abstraction()
                if file_storage:
                    # List files for this tenant/session
                    try:
                        files = await file_storage.list_files(
                            tenant_id=tenant_id,
                            prefix=f"session_{context.session_id}/"
                        )
                        files_uploaded = len(files) if files else 0
                        
                        # Get example files for tutorial
                        if files and len(files) > 0:
                            # Get first few files as examples
                            for file_info in files[:3]:
                                try:
                                    file_metadata = await file_storage.get_file_by_uuid(file_info.get("file_id") or file_info.get("uuid"))
                                    if file_metadata:
                                        file_examples.append({
                                            "file_name": file_metadata.get("ui_name") or file_metadata.get("filename", "Unknown"),
                                            "file_type": file_metadata.get("file_type", "Unknown"),
                                            "file_size": file_metadata.get("file_size", 0)
                                        })
                                except Exception as e:
                                    self.logger.debug(f"Could not get file metadata for example: {e}")
                    except Exception as e:
                        self.logger.warning(f"Could not list files: {e}")
        except Exception as e:
            self.logger.warning(f"Error gathering Content realm data: {e}")
        
        # Get counts from summary if available
        if content_summary:
            files_uploaded = content_summary.get("files_uploaded", files_uploaded)
            files_parsed = content_summary.get("files_parsed", files_parsed)
            deterministic_embeddings_count = content_summary.get("deterministic_embeddings", deterministic_embeddings_count)
            semantic_embeddings_count = content_summary.get("semantic_embeddings", semantic_embeddings_count)
            target_models_count = content_summary.get("target_models", target_models_count)
        
        # Build Data Mash Tutorial stages
        stages = [
            {
                "id": "ingestion",
                "name": "File Ingestion",
                "icon": "upload",
                "status": "complete" if files_uploaded > 0 else "pending",
                "count": files_uploaded,
                "tutorial": {
                    "what_happens": "Your files are uploaded to the platform and stored securely. The system identifies the file type (CSV, PDF, etc.) and prepares them for processing.",
                    "why_it_matters": "This is where your data journey begins. The platform needs to know what type of data you're working with before it can process it intelligently.",
                    "think_of_it_like": [
                        "The starting point of your data's journey",
                        "Like checking in at the airport before your flight"
                    ],
                    "example": {
                        "file_name": file_examples[0].get("file_name", "example_file.csv") if file_examples else "example_file.csv",
                        "file_type": file_examples[0].get("file_type", "Structured data (CSV format)") if file_examples else "Structured data (CSV format)",
                        "file_size": f"{file_examples[0].get('file_size', 0) / 1024:.1f} KB" if file_examples else "2.5 MB",
                        "status": "Ready for parsing"
                    }
                }
            },
            {
                "id": "parsing",
                "name": "File Parsing",
                "icon": "parse",
                "status": "complete" if files_parsed > 0 else "pending",
                "count": files_parsed,
                "tutorial": {
                    "what_happens": "The platform reads your files and extracts their structure and content. For structured data (like CSV), it identifies columns, data types, and relationships. For documents, it extracts text and identifies sections.",
                    "why_it_matters": "Parsing converts your raw files into a format the platform can understand and work with. It's like translating your data into a common language.",
                    "think_of_it_like": [
                        "Translating your data into a common language",
                        "Organizing a messy filing cabinet"
                    ],
                    "example": {
                        "before": {
                            "type": "raw_csv",
                            "preview": "name,age,city\nJohn,30,New York\nJane,25,Los Angeles"
                        },
                        "after": {
                            "type": "parsed_structure",
                            "columns": [
                                {"name": "name", "type": "text"},
                                {"name": "age", "type": "number"},
                                {"name": "city", "type": "text"}
                            ],
                            "row_count": files_parsed
                        }
                    }
                }
            },
            {
                "id": "deterministic_embedding",
                "name": "Deterministic Embedding",
                "icon": "brain",
                "status": "complete" if deterministic_embeddings_count > 0 else "pending",
                "count": deterministic_embeddings_count,
                "tutorial": {
                    "what_happens": "The platform creates a 'fingerprint' of your data's structure. This fingerprint captures the exact schema (columns, data types, patterns) in a way that can be reproduced exactly every time.",
                    "why_it_matters": "This fingerprint allows the platform to match your data to target models with precision. It's like creating a blueprint of your data structure that never changes, even if the actual data values do.",
                    "think_of_it_like": [
                        "A DNA fingerprint for your data structure",
                        "A blueprint that describes how your data is organized",
                        "A consistent way to identify and match data patterns"
                    ],
                    "example": {
                        "input_structure": {
                            "columns": ["name", "age", "city"],
                            "types": ["text", "number", "text"]
                        },
                        "output_fingerprint": {
                            "schema_fingerprint": "3_cols:text:num:text",
                            "pattern_signature": "name_age_location"
                        },
                        "explanation": "This fingerprint is always the same for this structure, making it perfect for exact matching."
                    }
                }
            },
            {
                "id": "interpreted_meaning",
                "name": "Interpreted Meaning",
                "icon": "lightbulb",
                "status": "complete" if semantic_embeddings_count > 0 else "pending",
                "count": semantic_embeddings_count,
                "tutorial": {
                    "what_happens": "The platform uses AI to understand the meaning and context of your data. It identifies what your data represents (customers, products, transactions, etc.) and how different pieces relate to each other.",
                    "why_it_matters": "This is where your data becomes 'smart.' The platform doesn't just see columns and rows - it understands what they mean and can help you find insights, make connections, and answer questions about your data.",
                    "think_of_it_like": [
                        "Reading between the lines to understand context",
                        "Connecting the dots to see relationships",
                        "Making your data searchable and queryable by meaning"
                    ],
                    "example": {
                        "data_structure": {
                            "columns": ["name", "age", "city"]
                        },
                        "interpreted_meaning": {
                            "data_type": "customer data",
                            "relationships": [
                                "name → person identity",
                                "age → demographic info",
                                "city → location data"
                            ],
                            "insights_available": [
                                "Customer demographics",
                                "Geographic distribution",
                                "Age-based segmentation"
                            ]
                        },
                        "example_queries": [
                            "Show me customers in New York",
                            "What's the average age?",
                            "Which cities have the most customers?"
                        ]
                    }
                }
            }
        ]
        
        # Build flow connections
        flow_connections = []
        if files_uploaded > 0:
            flow_connections.append({"from": "ingestion", "to": "parsing", "status": "complete" if files_parsed > 0 else "pending"})
        if files_parsed > 0:
            flow_connections.append({"from": "parsing", "to": "deterministic_embedding", "status": "complete" if deterministic_embeddings_count > 0 else "pending"})
        if deterministic_embeddings_count > 0:
            flow_connections.append({"from": "deterministic_embedding", "to": "interpreted_meaning", "status": "complete" if semantic_embeddings_count > 0 else "pending"})
        
        return {
            "realm": "content",
            "title": "Data Mash: How Your Data Transforms",
            "visual_type": "data_mash_tutorial",
            "primary_visual": {
                "type": "pipeline_flow",
                "stages": stages,
                "flow_connections": flow_connections
            },
            "secondary_metrics": {
                "files_uploaded": files_uploaded,
                "files_parsed": files_parsed,
                "target_models": target_models_count,
                "embedding_coverage": round((semantic_embeddings_count / files_uploaded * 100) if files_uploaded > 0 else 0, 1)
            },
            "status": "completed" if files_uploaded > 0 else "pending"
        }
    
    async def _generate_insights_visual(
        self,
        insights_summary: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate Insights pillar visual - Insights Ecosystem.
        
        Gathers real data from Insights realm.
        """
        # Get data from summary
        quality_score = insights_summary.get("overall_quality", 0.0) if insights_summary else 0.0
        mappings_count = insights_summary.get("mappings_count", 0) if insights_summary else 0
        insights_count = insights_summary.get("insights_count", 0) if insights_summary else 0
        relationships_count = insights_summary.get("relationships_count", 0) if insights_summary else 0
        
        # Get specialized pipeline data
        specialized_pipelines = {
            "pso": {
                "name": "Permits (PSO)",
                "icon": "permit",
                "active": insights_summary.get("pso_insights_count", 0) > 0 if insights_summary else False,
                "insights_count": insights_summary.get("pso_insights_count", 0) if insights_summary else 0,
                "status": "complete" if insights_summary.get("pso_insights_count", 0) > 0 else "pending"
            },
            "aar": {
                "name": "After Action Reports (AAR)",
                "icon": "report",
                "active": insights_summary.get("aar_insights_count", 0) > 0 if insights_summary else False,
                "insights_count": insights_summary.get("aar_insights_count", 0) if insights_summary else 0,
                "status": "complete" if insights_summary.get("aar_insights_count", 0) > 0 else "pending"
            },
            "variable_life": {
                "name": "Variable Life Policies",
                "icon": "policy",
                "active": insights_summary.get("variable_life_insights_count", 0) > 0 if insights_summary else False,
                "insights_count": insights_summary.get("variable_life_insights_count", 0) if insights_summary else 0,
                "status": "complete" if insights_summary.get("variable_life_insights_count", 0) > 0 else "pending"
            }
        }
        
        # Quality breakdown
        quality_breakdown = {
            "completeness": insights_summary.get("completeness_score", 0.0) if insights_summary else 0.0,
            "accuracy": insights_summary.get("accuracy_score", 0.0) if insights_summary else 0.0,
            "consistency": insights_summary.get("consistency_score", 0.0) if insights_summary else 0.0,
            "timeliness": insights_summary.get("timeliness_score", 0.0) if insights_summary else 0.0
        }
        
        return {
            "realm": "insights",
            "title": "Insights Pillar - Capabilities Showcase",
            "visual_type": "insights_ecosystem",
            "capabilities": {
                "quality_assessment": {
                    "overall_score": round(quality_score * 100, 1) if quality_score <= 1.0 else round(quality_score, 1),
                    "breakdown": quality_breakdown,
                    "status": "complete" if quality_score > 0 else "pending"
                },
                "business_analysis": {
                    "insights_count": insights_count,
                    "patterns_identified": insights_summary.get("patterns_count", 0) if insights_summary else 0,
                    "trends_detected": insights_summary.get("trends_count", 0) if insights_summary else 0,
                    "status": "complete" if insights_count > 0 else "pending"
                },
                "specialized_pipelines": specialized_pipelines,
                "relationship_graph": {
                    "nodes_count": relationships_count,
                    "edges_count": insights_summary.get("relationship_edges_count", 0) if insights_summary else 0,
                    "preview_size": "small",
                    "status": "complete" if relationships_count > 0 else "pending"
                }
            },
            "status": "completed" if insights_summary else "pending"
        }
    
    async def _generate_journey_visual(
        self,
        journey_summary: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate Journey pillar visual - Friction Removal Visualization.
        
        Gathers real data from Journey realm.
        """
        workflows_created = journey_summary.get("workflows_created", 0) if journey_summary else 0
        sops_generated = journey_summary.get("sops_generated", 0) if journey_summary else 0
        coexistence_analysis = journey_summary.get("coexistence_analysis", {}) if journey_summary else {}
        
        # Extract friction removal data from coexistence analysis
        friction_points_identified = coexistence_analysis.get("friction_points", []) if coexistence_analysis else []
        friction_points_removed = len([fp for fp in friction_points_identified if fp.get("resolved", False)]) if friction_points_identified else 0
        
        # Get coexistence breakdown
        human_tasks = coexistence_analysis.get("human_tasks_count", 0) if coexistence_analysis else 0
        ai_assisted_tasks = coexistence_analysis.get("ai_assisted_tasks_count", 0) if coexistence_analysis else 0
        hybrid_tasks = coexistence_analysis.get("hybrid_tasks_count", 0) if coexistence_analysis else 0
        total_tasks = human_tasks + ai_assisted_tasks + hybrid_tasks
        
        # Calculate percentages
        human_percentage = round((human_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        ai_percentage = round((ai_assisted_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        hybrid_percentage = round((hybrid_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        
        # Get workflow IDs for preview
        workflow_ids = journey_summary.get("workflow_ids", []) if journey_summary else []
        
        return {
            "realm": "journey",
            "title": "Journey Pillar - Coexistence Analysis",
            "visual_type": "friction_removal",
            "coexistence_analysis": {
                "friction_points_identified": len(friction_points_identified),
                "friction_points_removed": friction_points_removed,
                "human_focus_areas": human_tasks,
                "workflow_comparison": {
                    "before": {
                        "workflow_id": workflow_ids[0] if workflow_ids else None,
                        "friction_points": friction_points_identified[:3] if friction_points_identified else []
                    },
                    "after": {
                        "workflow_id": workflow_ids[-1] if len(workflow_ids) > 1 else workflow_ids[0] if workflow_ids else None,
                        "ai_assistance_points": [
                            fp for fp in friction_points_identified if fp.get("resolved", False)
                        ][:3]
                    }
                },
                "coexistence_breakdown": {
                    "human_tasks": human_percentage,
                    "ai_assisted_tasks": ai_percentage,
                    "hybrid_tasks": hybrid_percentage,
                    "total_tasks": total_tasks
                },
                "workflow_preview": {
                    "workflow_id": workflow_ids[0] if workflow_ids else None,
                    "status": "available" if workflow_ids else "pending"
                }
            },
            "status": "completed" if journey_summary else "pending"
        }
