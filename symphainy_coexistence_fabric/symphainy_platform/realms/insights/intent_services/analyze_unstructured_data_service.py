"""
Analyze Unstructured Data Intent Service

Implements the analyze_unstructured_data intent for the Insights Realm.

Contract: docs/intent_contracts/journey_insights_data_analysis/intent_analyze_unstructured_data.md

Purpose: Analyze unstructured data (text, documents, PDFs) for business insights.
Extracts themes, sentiments, key phrases, and actionable recommendations.

WHAT (Intent Service Role): I analyze unstructured data for business insights
HOW (Intent Service Implementation): I process unstructured text to extract
    themes, sentiments, and key information

Naming Convention:
- Realm: Insights Realm
- Artifacts: insights_unstructured_analysis
- Solution = platform construct (InsightsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class AnalyzeUnstructuredDataService(BaseIntentService):
    """
    Intent service for unstructured data analysis.
    
    Analyzes unstructured data (text, documents) for:
    - Theme extraction
    - Sentiment analysis
    - Key phrase extraction
    - Business insights generation
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize AnalyzeUnstructuredDataService."""
        super().__init__(
            service_id="analyze_unstructured_data_service",
            intent_type="analyze_unstructured_data",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the analyze_unstructured_data intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            parsed_file_id = intent_params.get("parsed_file_id")
            if not parsed_file_id:
                raise ValueError("parsed_file_id is required for unstructured analysis")
            
            analysis_options = intent_params.get("analysis_options", {})
            
            # Get parsed content
            parsed_content = await self._get_parsed_content(parsed_file_id, context)
            
            # Extract themes
            themes = await self._extract_themes(parsed_content)
            
            # Analyze sentiment
            sentiment = await self._analyze_sentiment(parsed_content)
            
            # Extract key phrases
            key_phrases = await self._extract_key_phrases(parsed_content)
            
            # Generate business insights
            business_insights = await self._generate_business_insights(
                themes, sentiment, key_phrases
            )
            
            # Build analysis result
            analysis_id = f"analysis_{generate_event_id()}"
            
            analysis = {
                "analysis_id": analysis_id,
                "parsed_file_id": parsed_file_id,
                "analysis_type": "unstructured",
                "themes": themes,
                "sentiment": sentiment,
                "key_phrases": key_phrases,
                "business_insights": business_insights,
                "content_summary": self._summarize_content(parsed_content),
                "analysis_options": analysis_options,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Artifact Plane
            artifact_id = await self._store_analysis(analysis, context)
            
            self.logger.info(f"Unstructured analysis completed: {analysis_id}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "analysis_id": analysis_id
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "analysis": analysis,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "unstructured_data_analyzed",
                        "analysis_id": analysis_id,
                        "analysis_type": "unstructured"
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _get_parsed_content(self, parsed_file_id: str, context: ExecutionContext) -> str:
        """Get parsed content from state surface or artifact plane."""
        if context.state_surface:
            try:
                data = await context.state_surface.get_execution_state(
                    key=f"parsed_file_{parsed_file_id}", tenant_id=context.tenant_id
                )
                if data:
                    return data.get("content", "") or str(data.get("records", []))
            except Exception:
                pass
        
        return ""
    
    async def _extract_themes(self, content: str) -> List[Dict[str, Any]]:
        """Extract themes from unstructured content."""
        themes = []
        
        if not content:
            return themes
        
        # Simple theme extraction based on word frequency
        words = content.lower().split()
        word_freq = {}
        
        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top themes
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        for i, (word, freq) in enumerate(sorted_words):
            themes.append({
                "theme_id": f"theme_{i}",
                "theme": word,
                "frequency": freq,
                "confidence": min(0.9, freq / max(len(words), 1) * 10)
            })
        
        return themes
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of unstructured content."""
        if not content:
            return {"sentiment": "neutral", "score": 0.5, "confidence": 0.0}
        
        # Simple sentiment analysis based on keywords
        positive_words = ["good", "great", "excellent", "positive", "success", "improve", "benefit"]
        negative_words = ["bad", "poor", "fail", "negative", "issue", "problem", "error"]
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return {"sentiment": "neutral", "score": 0.5, "confidence": 0.3}
        
        score = positive_count / total
        
        if score > 0.6:
            sentiment = "positive"
        elif score < 0.4:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "confidence": min(0.8, total / 10)
        }
    
    async def _extract_key_phrases(self, content: str) -> List[Dict[str, Any]]:
        """Extract key phrases from unstructured content."""
        key_phrases = []
        
        if not content:
            return key_phrases
        
        # Simple phrase extraction (2-3 word combinations)
        words = content.split()
        
        for i in range(len(words) - 1):
            if len(words[i]) > 3 and len(words[i+1]) > 3:
                phrase = f"{words[i]} {words[i+1]}"
                key_phrases.append({
                    "phrase": phrase,
                    "position": i,
                    "confidence": 0.6
                })
        
        return key_phrases[:20]  # Limit to top 20
    
    def _summarize_content(self, content: str) -> Dict[str, Any]:
        """Generate content summary."""
        if not content:
            return {"word_count": 0, "character_count": 0}
        
        words = content.split()
        sentences = content.split(".")
        
        return {
            "word_count": len(words),
            "character_count": len(content),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 1)
        }
    
    async def _generate_business_insights(
        self,
        themes: List[Dict[str, Any]],
        sentiment: Dict[str, Any],
        key_phrases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate business insights from analysis."""
        insights = []
        recommendations = []
        
        # Insights from themes
        if themes:
            top_themes = [t["theme"] for t in themes[:3]]
            insights.append(f"Main themes: {', '.join(top_themes)}")
        
        # Insights from sentiment
        sentiment_label = sentiment.get("sentiment", "neutral")
        if sentiment_label == "positive":
            insights.append("Overall sentiment is positive")
        elif sentiment_label == "negative":
            insights.append("Overall sentiment is negative")
            recommendations.append("Review content for improvement opportunities")
        
        # Insights from key phrases
        if key_phrases:
            insights.append(f"Identified {len(key_phrases)} key phrases")
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "sentiment_score": sentiment.get("score", 0.5),
            "analysis_confidence": 0.7
        }
    
    async def _store_analysis(self, analysis: Dict[str, Any], context: ExecutionContext) -> Optional[str]:
        """Store analysis in Artifact Plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.create_artifact(
                        artifact_type="analysis_report",
                        content=analysis,
                        metadata={"analysis_type": "unstructured"},
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store analysis: {e}")
        return None
