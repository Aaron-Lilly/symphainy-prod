"""
Unstructured Analysis Service - Enhanced Unstructured Data Analysis

Enabling service for unstructured data analysis operations.

WHAT (Enabling Service Role): I analyze unstructured data
HOW (Enabling Service Implementation): I perform semantic, sentiment, topic, and extraction analysis

Key Principle: Pure data processing - semantic and linguistic analysis on unstructured data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from collections import Counter
import re

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext


class UnstructuredAnalysisService:
    """
    Unstructured Analysis Service - Enhanced unstructured data analysis.
    
    Performs:
    - Semantic analysis (meaning, context, relationships)
    - Sentiment analysis (positive, negative, neutral)
    - Topic modeling (main topics, themes)
    - Entity extraction (people, places, organizations, etc.)
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Unstructured Analysis Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
    
    async def analyze_unstructured_data(
        self,
        parsed_file_id: str,
        analysis_options: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Analyze unstructured data with enhanced capabilities.
        
        Args:
            parsed_file_id: Parsed file identifier
            analysis_options: Analysis options (semantic, sentiment, topics, extraction, deep_dive)
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with unstructured analysis results
        """
        self.logger.info(
            f"Analyzing unstructured data: {parsed_file_id} for tenant: {tenant_id}"
        )
        
        try:
            # Get parsed data from State Surface
            parsed_data = await self._get_parsed_data(parsed_file_id, context)
            
            if not parsed_data:
                return {
                    "parsed_file_id": parsed_file_id,
                    "error": "No parsed data available",
                    "semantic_analysis": {},
                    "sentiment_analysis": {},
                    "topic_modeling": {},
                    "entity_extraction": {},
                    "deep_dive": None
                }
            
            results = {
                "parsed_file_id": parsed_file_id,
                "semantic_analysis": {},
                "sentiment_analysis": {},
                "topic_modeling": {},
                "entity_extraction": {},
                "deep_dive": None
            }
            
            # Semantic analysis
            if analysis_options.get("semantic", True):
                results["semantic_analysis"] = await self._perform_semantic_analysis(
                    parsed_data
                )
            
            # Sentiment analysis
            if analysis_options.get("sentiment", True):
                results["sentiment_analysis"] = await self._perform_sentiment_analysis(
                    parsed_data
                )
            
            # Topic modeling
            if analysis_options.get("topics", True):
                results["topic_modeling"] = await self._perform_topic_modeling(
                    parsed_data
                )
            
            # Entity extraction
            if analysis_options.get("extraction", True):
                results["entity_extraction"] = await self._extract_entities(
                    parsed_data
                )
            
            # Deep dive (Insights Liaison Agent)
            if analysis_options.get("deep_dive", False):
                results["deep_dive"] = await self._initiate_deep_dive(
                    parsed_file_id, parsed_data, tenant_id, context
                )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to analyze unstructured data: {e}", exc_info=True)
            return {
                "parsed_file_id": parsed_file_id,
                "error": str(e),
                "semantic_analysis": {},
                "sentiment_analysis": {},
                "topic_modeling": {},
                "entity_extraction": {},
                "deep_dive": None
            }
    
    async def _get_parsed_data(
        self,
        parsed_file_id: str,
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """Get parsed data from State Surface."""
        if hasattr(context, 'state_surface') and context.state_surface:
            try:
                # Construct parsed file reference
                parsed_file_reference = f"parsed:{context.tenant_id}:{context.session_id}:{parsed_file_id}"
                # ARCHITECTURAL PRINCIPLE: Use Content Realm service for file retrieval (governed access)
                # Never use state_surface.get_file() or state_surface.retrieve_file() - that's an anti-pattern.
                if not self.public_works:
                    self.logger.warning("Public Works not available - cannot retrieve parsed file via Content Realm")
                    return None
                
                # Use Content Realm service (governed access)
                from symphainy_platform.realms.content.enabling_services.file_parser_service import FileParserService
                file_parser_service = FileParserService(public_works=self.public_works)
                
                # Extract parsed_file_id from reference if needed
                parsed_file_id = parsed_file_reference.split(':')[-1] if ':' in parsed_file_reference else parsed_file_reference
                
                parsed_file = await file_parser_service.get_parsed_file(
                    parsed_file_id=parsed_file_id,
                    tenant_id=context.tenant_id,
                    context=context
                )
                
                parsed_content = parsed_file.get("parsed_content")
                if parsed_content:
                    import json
                    if isinstance(parsed_content, (dict, list)):
                        return parsed_content
                    elif isinstance(parsed_content, str):
                        try:
                            return json.loads(parsed_content)
                        except json.JSONDecodeError:
                            return parsed_content
                    return parsed_content
            except Exception as e:
                self.logger.debug(f"Could not retrieve parsed data via Content Realm: {e}")
        
        return None
    
    async def _perform_semantic_analysis(
        self,
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform semantic analysis on unstructured data.
        
        Analyzes: meaning, context, relationships, themes
        """
        semantic = {
            "themes": [],
            "key_concepts": [],
            "relationships": [],
            "context": {}
        }
        
        # Extract text content
        text_content = parsed_data.get("text_content", "")
        if not text_content:
            # Try to extract from structured data
            structured_data = parsed_data.get("structured_data", {})
            if isinstance(structured_data, dict):
                text_content = str(structured_data)
        
        if not text_content:
            return {"message": "No text content available for semantic analysis"}
        
        # Simple keyword extraction (full implementation would use embeddings/NLP)
        words = re.findall(r'\b\w+\b', text_content.lower())
        word_freq = Counter(words)
        
        # Extract key concepts (most frequent meaningful words)
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "should", "could", "may", "might", "must", "can"}
        meaningful_words = [(word, count) for word, count in word_freq.most_common(20) if word not in stop_words and len(word) > 3]
        
        semantic["key_concepts"] = [{"concept": word, "frequency": count} for word, count in meaningful_words]
        
        # Extract themes (simplified - full implementation would use topic modeling)
        semantic["themes"] = [
            {"theme": "General content", "confidence": 0.7, "keywords": [w[0] for w in meaningful_words[:5]]}
        ]
        
        return semantic
    
    async def _perform_sentiment_analysis(
        self,
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform sentiment analysis on unstructured data.
        
        Analyzes: positive, negative, neutral sentiment
        """
        sentiment = {
            "overall_sentiment": "neutral",
            "sentiment_score": 0.0,
            "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0}
        }
        
        # Extract text content
        text_content = parsed_data.get("text_content", "")
        if not text_content:
            structured_data = parsed_data.get("structured_data", {})
            if isinstance(structured_data, dict):
                text_content = str(structured_data)
        
        if not text_content:
            return {"message": "No text content available for sentiment analysis"}
        
        # Simple sentiment analysis (full implementation would use NLP models)
        positive_words = ["good", "great", "excellent", "positive", "success", "improve", "benefit", "advantage", "favorable"]
        negative_words = ["bad", "poor", "negative", "failure", "problem", "issue", "error", "disadvantage", "unfavorable"]
        
        text_lower = text_content.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words > 0:
            sentiment["sentiment_score"] = (positive_count - negative_count) / total_sentiment_words
            if sentiment["sentiment_score"] > 0.2:
                sentiment["overall_sentiment"] = "positive"
            elif sentiment["sentiment_score"] < -0.2:
                sentiment["overall_sentiment"] = "negative"
            else:
                sentiment["overall_sentiment"] = "neutral"
        
        sentiment["sentiment_distribution"] = {
            "positive": positive_count,
            "negative": negative_count,
            "neutral": max(0, len(text_content.split()) - positive_count - negative_count)
        }
        
        return sentiment
    
    async def _perform_topic_modeling(
        self,
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform topic modeling on unstructured data.
        
        Identifies: main topics, themes, subject areas
        """
        topics = {
            "main_topics": [],
            "topic_distribution": {},
            "themes": []
        }
        
        # Extract text content
        text_content = parsed_data.get("text_content", "")
        if not text_content:
            structured_data = parsed_data.get("structured_data", {})
            if isinstance(structured_data, dict):
                text_content = str(structured_data)
        
        if not text_content:
            return {"message": "No text content available for topic modeling"}
        
        # Simple topic extraction (full implementation would use LDA/NMF)
        words = re.findall(r'\b\w+\b', text_content.lower())
        word_freq = Counter(words)
        
        # Extract most common words as topics
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        meaningful_words = [(word, count) for word, count in word_freq.most_common(15) if word not in stop_words and len(word) > 3]
        
        topics["main_topics"] = [
            {"topic": word, "frequency": count, "weight": count / len(words) if words else 0}
            for word, count in meaningful_words[:5]
        ]
        
        topics["topic_distribution"] = {word: count for word, count in meaningful_words}
        
        return topics
    
    async def _extract_entities(
        self,
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract entities from unstructured data.
        
        Extracts: people, places, organizations, dates, etc.
        """
        entities = {
            "people": [],
            "places": [],
            "organizations": [],
            "dates": [],
            "other": []
        }
        
        # Extract text content
        text_content = parsed_data.get("text_content", "")
        if not text_content:
            structured_data = parsed_data.get("structured_data", {})
            if isinstance(structured_data, dict):
                text_content = str(structured_data)
        
        if not text_content:
            return {"message": "No text content available for entity extraction"}
        
        # Simple entity extraction (full implementation would use NER models)
        # Extract potential dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        dates = re.findall(date_pattern, text_content)
        entities["dates"] = list(set(dates))[:10]
        
        # Extract potential organizations (words with capital letters)
        org_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_orgs = re.findall(org_pattern, text_content)
        entities["organizations"] = list(set(potential_orgs))[:10]
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text_content)
        entities["other"].extend([{"type": "email", "value": email} for email in emails[:10]])
        
        return entities
    
    async def _initiate_deep_dive(
        self,
        parsed_file_id: str,
        parsed_data: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Initiate deep dive investigation via Insights Liaison Agent.
        
        ARCHITECTURAL PRINCIPLE: Uses Insights Liaison Agent for interactive analysis.
        """
        self.logger.info(f"Initiating deep dive for {parsed_file_id} via Insights Liaison Agent")
        
        try:
            # Get or create Insights Liaison Agent
            from ..agents.insights_liaison_agent import InsightsLiaisonAgent
            
            if not hasattr(self, 'insights_liaison_agent') or not self.insights_liaison_agent:
                self.insights_liaison_agent = InsightsLiaisonAgent(public_works=self.public_works)
            
            # Get analysis results for this parsed file
            analysis_results = parsed_data.get("analysis_results", {})
            
            # Initiate deep dive session via agent
            session_result = await self.insights_liaison_agent.initiate_deep_dive(
                parsed_file_id=parsed_file_id,
                analysis_results=analysis_results,
                tenant_id=tenant_id,
                context=context
            )
            
            return {
                "agent_engaged": True,
                "agent_type": "insights_liaison",
                "status": "ready",
                "session_id": session_result.get("session_id"),
                "message": session_result.get("message", "Deep dive investigation initiated. Agent will analyze data and provide insights."),
                "capabilities": session_result.get("capabilities", [])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initiate deep dive: {e}", exc_info=True)
            return {
                "agent_engaged": False,
                "agent_type": "insights_liaison",
                "status": "error",
                "message": f"Failed to initiate deep dive: {str(e)}",
                "error": str(e)
            }
