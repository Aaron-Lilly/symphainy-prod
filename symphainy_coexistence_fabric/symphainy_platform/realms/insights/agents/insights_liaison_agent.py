"""
Insights Liaison Agent - Interactive Deep Dive Analysis Agent

Agent for interactive deep dive analysis of data insights.

WHAT (Agent Role): I provide interactive deep dive analysis
HOW (Agent Implementation): I reason about data, answer questions, explore relationships

Key Principle: Agentic reasoning - uses embeddings and analysis results to provide insights.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime

from utilities import get_logger, generate_event_id
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
from symphainy_platform.civic_systems.agentic.models.agent_runtime_context import AgentRuntimeContext
from symphainy_platform.civic_systems.agentic.agents.stateless_embedding_agent import StatelessEmbeddingAgent


class InsightsLiaisonAgent(AgentBase):
    """
    Insights Liaison Agent - Interactive deep dive analysis.
    
    Provides:
    - Interactive analysis session
    - Question answering about data
    - Relationship exploration
    - Pattern identification
    - Recommendations
    """
    
    def __init__(self, public_works: Optional[Any] = None, **kwargs):
        """
        Initialize Insights Liaison Agent.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
            **kwargs: Additional parameters for 4-layer model support
        """
        # Initialize AgentBase
        super().__init__(
            agent_id="insights_liaison_agent",
            agent_type="insights_liaison",
            capabilities=["answer_questions", "explore_relationships", "identify_patterns", "provide_recommendations"],
            public_works=public_works,
            **kwargs
        )
        
        # Get abstractions from Public Works
        self.semantic_data_abstraction = None
        if public_works:
            self.semantic_data_abstraction = public_works.get_semantic_data_abstraction()
        
        # Create StatelessEmbeddingAgent for embedding operations
        self.embedding_agent = None
        if public_works:
            self.embedding_agent = StatelessEmbeddingAgent(
                agent_id="insights_liaison_embedding_agent",
                public_works=public_works
            )
        
        # PHASE 3: Initialize chunking, parsing, and semantic signal services
        self.deterministic_chunking_service = None
        self.file_parser_service = None
        self.semantic_signal_extractor = None
        if public_works:
            from symphainy_platform.foundations.libraries.chunking.deterministic_chunking_service import DeterministicChunkingService
            from symphainy_platform.foundations.libraries.parsing.file_parser_service import FileParserService
            from symphainy_platform.civic_systems.agentic.agents.semantic_signal_extractor import SemanticSignalExtractor
            self.deterministic_chunking_service = DeterministicChunkingService(public_works=public_works)
            self.file_parser_service = FileParserService(public_works=public_works)
            self.semantic_signal_extractor = SemanticSignalExtractor(public_works=public_works)
    
    async def _process_with_assembled_prompt(
        self,
        system_message: str,
        user_message: str,
        runtime_context: AgentRuntimeContext,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request with assembled prompt (4-layer model).
        
        This method is called by AgentBase.process_request() after assembling
        the system and user messages from the 4-layer model.
        
        Args:
            system_message: Assembled system message (from layers 1-3)
            user_message: Assembled user message
            runtime_context: Runtime context with business_context
            context: Execution context
        
        Returns:
            Dict with analysis result
        """
        # Extract request type and parameters from user_message
        # Try to parse as JSON first
        request_data = {}
        try:
            import json
            if user_message.strip().startswith("{"):
                request_data = json.loads(user_message)
            else:
                # Try to extract from runtime_context.business_context
                if hasattr(runtime_context, 'business_context') and runtime_context.business_context:
                    request_data = runtime_context.business_context.get("request", {})
                # If still empty, treat user_message as question
                if not request_data:
                    request_data = {"type": "answer_question", "question": user_message.strip()}
        except (json.JSONDecodeError, ValueError):
            # Fallback: treat as question
            request_data = {"type": "answer_question", "question": user_message.strip()}
        
        # Route to appropriate method based on request type
        request_type = request_data.get("type", "answer_question")
        session_id = request_data.get("session_id", context.session_id)
        
        if request_type == "answer_question":
            return await self.answer_question(
                session_id=session_id,
                question=request_data.get("question", user_message.strip()),
                tenant_id=context.tenant_id,
                context=context
            )
        elif request_type == "explore_relationships":
            return await self.explore_relationships(
                session_id=session_id,
                entity=request_data.get("entity"),
                tenant_id=context.tenant_id,
                context=context
            )
        elif request_type == "identify_patterns":
            return await self.identify_patterns(
                session_id=session_id,
                pattern_type=request_data.get("pattern_type"),
                tenant_id=context.tenant_id,
                context=context
            )
        elif request_type == "provide_recommendations":
            return await self.provide_recommendations(
                session_id=session_id,
                recommendation_type=request_data.get("recommendation_type"),
                tenant_id=context.tenant_id,
                context=context
            )
        else:
            # Default to answer_question if type unknown
            return await self.answer_question(
                session_id=session_id,
                question=user_message.strip(),
                tenant_id=context.tenant_id,
                context=context
            )
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext,
        runtime_context: Optional[AgentRuntimeContext] = None
    ) -> Dict[str, Any]:
        """
        Process agent request (required by AgentBase).
        
        ARCHITECTURAL PRINCIPLE: This method delegates to AgentBase.process_request()
        which implements the 4-layer model. For backward compatibility, it can also
        be called directly, but the 4-layer flow is preferred.
        """
        # If runtime_context is provided, use it; otherwise let AgentBase assemble it
        if runtime_context:
            system_message = self._assemble_system_message(runtime_context)
            user_message = self._assemble_user_message(request, runtime_context)
            return await self._process_with_assembled_prompt(
                system_message, user_message, runtime_context, context
            )
        else:
            # Delegate to parent's process_request which implements 4-layer model
            return await super().process_request(request, context, runtime_context=None)
    
    async def get_agent_description(self) -> str:
        """Get agent description (required by AgentBase)."""
        return "Insights Liaison Agent - Provides interactive deep dive analysis of data insights"
    
    async def initiate_deep_dive(
        self,
        parsed_file_id: str,
        analysis_results: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Initiate deep dive investigation session.
        
        Args:
            parsed_file_id: Parsed file identifier
            analysis_results: Results from structured/unstructured analysis
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with deep dive session information
        """
        self.logger.info(
            f"Initiating deep dive for {parsed_file_id} via Insights Liaison Agent"
        )
        
        session_id = generate_event_id()
        
        # Store session context in execution context metadata
        # This allows other methods to access parsed_file_id and analysis_results
        session_key = f"deep_dive_session_{session_id}"
        context.metadata[session_key] = {
            "parsed_file_id": parsed_file_id,
            "analysis_results": analysis_results,
            "tenant_id": tenant_id,
            "created_at": datetime.utcnow().isoformat() if hasattr(datetime, 'utcnow') else str(datetime.now())
        }
        
        self.logger.info(f"✅ Deep dive session created: {session_id} for parsed_file_id: {parsed_file_id}")
        
        return {
            "session_id": session_id,
            "parsed_file_id": parsed_file_id,
            "agent_type": "insights_liaison",
            "status": "ready",
            "capabilities": [
                "answer_questions",
                "explore_relationships",
                "identify_patterns",
                "provide_recommendations"
            ],
            "message": "Deep dive session initiated. Ready for interactive analysis."
        }
    
    async def answer_question(
        self,
        session_id: str,
        question: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Answer a question about the data.
        
        ARCHITECTURAL PRINCIPLE: Uses embeddings and LLM via Public Works abstractions.
        
        Args:
            session_id: Deep dive session identifier
            question: User question
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with answer and supporting evidence
        """
        self.logger.info(f"Answering question in session {session_id}: {question}")
        
        try:
            # 1. Get session context (stored in context metadata or state surface)
            session_context = context.metadata.get(f"deep_dive_session_{session_id}", {})
            parsed_file_id = session_context.get("parsed_file_id")
            analysis_results = session_context.get("analysis_results", {})
            
            if not parsed_file_id:
                return {
                    "session_id": session_id,
                    "question": question,
                    "answer": "Session context not found. Please initiate a deep dive session first.",
                    "confidence": 0.0,
                    "evidence": []
                }
            
            # 2. Use embeddings to find relevant data
            relevant_data = []
            if self.semantic_data_abstraction and self.embedding_agent:
                try:
                    # Generate embedding for the question
                    question_embedding_result = await self.embedding_agent.generate_embedding(
                        text=question,
                        context=context
                    )
                    question_embedding = question_embedding_result.get("embedding", [])
                    
                    if question_embedding:
                        # Search for similar embeddings
                        similar_embeddings = await self.semantic_data_abstraction.search_similar_embeddings(
                            query_embedding=question_embedding,
                            filter_conditions={"parsed_file_id": parsed_file_id},
                            limit=5,
                            tenant_id=tenant_id
                        )
                        
                        # Extract relevant data from similar embeddings
                        for emb in similar_embeddings:
                            relevant_data.append({
                                "column_name": emb.get("column_name"),
                                "semantic_meaning": emb.get("semantic_meaning"),
                                "sample_values": emb.get("sample_values", [])[:3],
                                "similarity": emb.get("similarity_score", 0.0)
                            })
                except Exception as e:
                    self.logger.warning(f"Failed to search embeddings: {e}")
            
            # 3. Reason about question using analysis results and relevant data
            answer = ""
            evidence = []
            
            if self.public_works:
                try:
                    # Prepare context for LLM
                    context_text = f"Analysis Results:\n{str(analysis_results)[:1000]}\n\n"
                    if relevant_data:
                        context_text += "Relevant Data:\n"
                        for data in relevant_data[:3]:
                            context_text += f"- {data.get('column_name')}: {data.get('semantic_meaning')}\n"
                    
                    system_message = """You are an expert data analyst helping users understand their data.
                    
Use the provided analysis results and relevant data to answer the user's question accurately.
Provide specific, actionable answers based on the data.
If you don't have enough information, say so clearly."""
                    
                    user_prompt = f"""Context:
{context_text}

Question: {question}

Provide a clear, specific answer based on the available data."""
                    
                    # Use agent._call_llm() for governed LLM access
                    answer = await self._call_llm(
                        prompt=user_prompt,
                        system_message=system_message,
                        model="gpt-4o-mini",
                        max_tokens=500,
                        temperature=0.3,
                        context=context
                    )
                    
                    # Extract evidence from relevant data
                    evidence = [
                        {
                            "source": f"Column: {data.get('column_name')}",
                            "meaning": data.get("semantic_meaning"),
                            "relevance": data.get("similarity", 0.0)
                        }
                        for data in relevant_data[:3]
                    ]
                    
                except Exception as e:
                    self.logger.warning(f"Failed to generate answer via LLM: {e}")
                    answer = f"Based on the analysis results, I can see relevant data but encountered an error generating a detailed answer. Please try rephrasing your question."
            
            if not answer:
                # Fallback answer
                answer = "I need more context to answer this question. Please ensure analysis results are available."
            
            # Calculate confidence based on evidence quality
            confidence = min(0.9, 0.5 + (len(evidence) * 0.1) + (max([e.get("relevance", 0.0) for e in evidence] + [0.0]) * 0.3))
            
            return {
                "session_id": session_id,
                "question": question,
                "answer": answer.strip(),
                "confidence": confidence,
                "evidence": evidence,
                "relevant_data_count": len(relevant_data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to answer question: {e}", exc_info=True)
            return {
                "session_id": session_id,
                "question": question,
                "answer": f"An error occurred while processing your question: {str(e)}",
                "confidence": 0.0,
                "evidence": []
            }
    
    async def explore_relationships(
        self,
        session_id: str,
        entity: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Explore relationships for a given entity.
        
        ARCHITECTURAL PRINCIPLE: Uses SemanticDataAbstraction for graph queries.
        
        Args:
            session_id: Deep dive session identifier
            entity: Entity to explore
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with relationships and connections
        """
        self.logger.info(f"Exploring relationships for {entity} in session {session_id}")
        
        try:
            # Get session context
            session_context = context.metadata.get(f"deep_dive_session_{session_id}", {})
            parsed_file_id = session_context.get("parsed_file_id")
            
            relationships = []
            connected_entities = []
            
            if self.semantic_data_abstraction and parsed_file_id:
                try:
                    # PHASE 3: Use chunk-based pattern
                    # 1. Get parsed file and create chunks
                    parsed_file = await self.file_parser_service.get_parsed_file(
                        parsed_file_id=parsed_file_id,
                        tenant_id=tenant_id,
                        context=context
                    )
                    
                    parsed_content = parsed_file.get("parsed_content") or parsed_file
                    chunks = await self.deterministic_chunking_service.create_chunks(
                        parsed_content=parsed_content,
                        file_id=parsed_file.get("file_id"),
                        tenant_id=tenant_id,
                        parsed_file_id=parsed_file_id
                    )
                    
                    # 2. Query semantic graph for entity relationships
                    # Search for embeddings related to the entity
                    if self.embedding_agent and chunks:
                        entity_embedding_result = await self.embedding_agent.generate_embedding(
                            text=entity,
                            context=context
                        )
                        entity_embedding = entity_embedding_result.get("embedding", [])
                        
                        if entity_embedding:
                            # 3. Find similar entities by chunk_id (not parsed_file_id)
                            chunk_ids = [chunk.chunk_id for chunk in chunks]
                            similar_entities = await self.semantic_data_abstraction.search_similar_embeddings(
                                query_embedding=entity_embedding,
                                filter_conditions={"chunk_id": {"$in": chunk_ids}},
                                limit=10,
                                tenant_id=tenant_id
                            )
                            
                            # 4. Build relationship network
                            for similar in similar_entities:
                                col_name = similar.get("column_name") or similar.get("metadata", {}).get("column_name")
                                if col_name and col_name != entity:
                                    connected_entities.append(col_name)
                                    relationships.append({
                                        "source": entity,
                                        "target": col_name,
                                        "relationship_type": "semantic_similarity",
                                        "confidence": similar.get("similarity_score", 0.0),
                                        "description": f"Semantically similar to {entity}"
                                    })
                except Exception as e:
                    self.logger.warning(f"Failed to query relationships: {e}")
            
            # Use LLM to infer relationship types if available
            if self.public_works and relationships:
                try:
                    relationships_text = "\n".join([
                        f"- {r['source']} -> {r['target']} ({r['relationship_type']})"
                        for r in relationships[:5]
                    ])
                    
                    system_message = """You are a data analyst identifying relationships between data entities.
Analyze the relationships and suggest relationship types (e.g., 'contains', 'references', 'derived_from')."""
                    
                    user_prompt = f"""Entity: {entity}
Relationships found:
{relationships_text}

Suggest more specific relationship types for these connections."""
                    
                    llm_suggestions = await self._call_llm(
                        prompt=user_prompt,
                        system_message=system_message,
                        model="gpt-4o-mini",
                        max_tokens=200,
                        temperature=0.3,
                        context=context
                    )
                    
                    # Parse LLM suggestions and enhance relationships
                    # (Simplified - in production would parse structured output)
                    for rel in relationships[:3]:
                        rel["llm_enhanced_type"] = "semantic_connection"
                        
                except Exception as e:
                    self.logger.debug(f"LLM relationship enhancement failed: {e}")
            
            return {
                "session_id": session_id,
                "entity": entity,
                "relationships": relationships,
                "connected_entities": list(set(connected_entities)),
                "relationship_count": len(relationships)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to explore relationships: {e}", exc_info=True)
            return {
                "session_id": session_id,
                "entity": entity,
                "relationships": [],
                "connected_entities": [],
                "error": str(e)
            }
    
    async def identify_patterns(
        self,
        session_id: str,
        pattern_type: Optional[str],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Identify patterns in the data.
        
        ARCHITECTURAL PRINCIPLE: Uses analysis results and LLM for pattern detection.
        
        Args:
            session_id: Deep dive session identifier
            pattern_type: Optional pattern type filter
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with identified patterns
        """
        self.logger.info(f"Identifying patterns in session {session_id}")
        
        try:
            # Get session context
            session_context = context.metadata.get(f"deep_dive_session_{session_id}", {})
            parsed_file_id = session_context.get("parsed_file_id")
            analysis_results = session_context.get("analysis_results", {})
            
            patterns = []
            pattern_types = []
            
            # Analyze data for patterns using LLM
            if self.public_works and analysis_results:
                try:
                    # Prepare analysis summary
                    analysis_summary = str(analysis_results)[:2000]  # Limit context
                    
                    system_message = """You are a data analyst identifying patterns in data.
Identify recurring patterns, sequences, correlations, and anomalies.
Return a structured list of patterns with descriptions."""
                    
                    pattern_analysis_prompt = f"""Analysis Results:
{analysis_summary}

Identify patterns in this data. Look for:
- Recurring sequences
- Correlations between fields
- Anomalies or outliers
- Data quality patterns
- Business logic patterns

Return a list of identified patterns with brief descriptions."""
                    
                    if pattern_type:
                        pattern_analysis_prompt += f"\n\nFocus on pattern type: {pattern_type}"
                    
                    pattern_analysis = await self._call_llm(
                        prompt=pattern_analysis_prompt,
                        system_message=system_message,
                        model="gpt-4o-mini",
                        max_tokens=500,
                        temperature=0.3,
                        context=context
                    )
                    
                    # Parse patterns from LLM response (simplified - in production would use structured output)
                    # Extract pattern descriptions
                    pattern_lines = pattern_analysis.split('\n')
                    for line in pattern_lines:
                        if line.strip() and ('pattern' in line.lower() or 'correlation' in line.lower() or 'anomaly' in line.lower()):
                            patterns.append({
                                "description": line.strip(),
                                "type": pattern_type or "general",
                                "confidence": 0.7
                            })
                            if pattern_type:
                                pattern_types.append(pattern_type)
                            else:
                                pattern_types.append("general")
                    
                    # If no patterns found, create a summary pattern
                    if not patterns:
                        patterns.append({
                            "description": "Data analysis completed. Review analysis results for detailed insights.",
                            "type": "summary",
                            "confidence": 0.8
                        })
                        pattern_types.append("summary")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to identify patterns via LLM: {e}")
                    patterns.append({
                        "description": "Pattern analysis encountered an error. Review analysis results manually.",
                        "type": "error",
                        "confidence": 0.0
                    })
            
            # Remove duplicates
            unique_patterns = []
            seen = set()
            for pattern in patterns:
                desc = pattern.get("description", "")
                if desc and desc not in seen:
                    seen.add(desc)
                    unique_patterns.append(pattern)
            
            return {
                "session_id": session_id,
                "patterns": unique_patterns,
                "pattern_types": list(set(pattern_types)),
                "pattern_count": len(unique_patterns)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to identify patterns: {e}", exc_info=True)
            return {
                "session_id": session_id,
                "patterns": [],
                "pattern_types": [],
                "error": str(e)
            }
    
    async def provide_recommendations(
        self,
        session_id: str,
        recommendation_type: Optional[str],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Provide recommendations based on analysis.
        
        ARCHITECTURAL PRINCIPLE: Uses analysis results and LLM for recommendation generation.
        
        Args:
            session_id: Deep dive session identifier
            recommendation_type: Optional recommendation type filter
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with recommendations
        """
        self.logger.info(f"Providing recommendations in session {session_id}")
        
        try:
            # Get session context
            session_context = context.metadata.get(f"deep_dive_session_{session_id}", {})
            parsed_file_id = session_context.get("parsed_file_id")
            analysis_results = session_context.get("analysis_results", {})
            
            recommendations = []
            priority = "medium"
            
            # Generate recommendations using LLM
            if self.public_works and analysis_results:
                try:
                    # Prepare analysis summary
                    analysis_summary = str(analysis_results)[:2000]
                    
                    system_message = """You are a data analyst providing actionable recommendations.
Analyze the data findings and provide specific, actionable recommendations for improvement.
Prioritize recommendations by impact (high, medium, low)."""
                    
                    recommendation_prompt = f"""Analysis Results:
{analysis_summary}

Based on this analysis, provide actionable recommendations for:
- Data quality improvements
- Process optimizations
- Business insights
- Technical improvements

Return recommendations with priority levels (high, medium, low)."""
                    
                    if recommendation_type:
                        recommendation_prompt += f"\n\nFocus on recommendation type: {recommendation_type}"
                    
                    recommendation_text = await self._call_llm(
                        prompt=recommendation_prompt,
                        system_message=system_message,
                        model="gpt-4o-mini",
                        max_tokens=600,
                        temperature=0.3,
                        context=context
                    )
                    
                    # Parse recommendations from LLM response
                    rec_lines = recommendation_text.split('\n')
                    current_priority = "medium"
                    for line in rec_lines:
                        line_lower = line.lower()
                        if 'high priority' in line_lower or 'critical' in line_lower:
                            current_priority = "high"
                        elif 'low priority' in line_lower or 'minor' in line_lower:
                            current_priority = "low"
                        
                        if line.strip() and ('recommend' in line_lower or 'suggest' in line_lower or 'should' in line_lower or line.strip().startswith('-')):
                            rec_text = line.strip().lstrip('-').strip()
                            if rec_text and len(rec_text) > 10:
                                recommendations.append({
                                    "recommendation": rec_text,
                                    "priority": current_priority,
                                    "type": recommendation_type or "general",
                                    "impact": "medium"
                                })
                    
                    # Determine overall priority
                    if any(r.get("priority") == "high" for r in recommendations):
                        priority = "high"
                    elif any(r.get("priority") == "low" for r in recommendations):
                        priority = "low"
                    
                    # If no recommendations found, create a general one
                    if not recommendations:
                        recommendations.append({
                            "recommendation": "Review the analysis results in detail to identify specific improvement opportunities.",
                            "priority": "medium",
                            "type": "general",
                            "impact": "medium"
                        })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to generate recommendations via LLM: {e}")
                    recommendations.append({
                        "recommendation": "Review analysis results manually to identify improvement opportunities.",
                        "priority": "medium",
                        "type": "general",
                        "impact": "medium"
                    })
            
            return {
                "session_id": session_id,
                "recommendations": recommendations,
                "priority": priority,
                "recommendation_count": len(recommendations)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to provide recommendations: {e}", exc_info=True)
            return {
                "session_id": session_id,
                "recommendations": [],
                "priority": "medium",
                "error": str(e)
            }
