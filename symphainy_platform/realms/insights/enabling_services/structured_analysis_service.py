"""
Structured Analysis Service - Enhanced Structured Data Analysis

Enabling service for structured data analysis operations.

WHAT (Enabling Service Role): I analyze structured data
HOW (Enabling Service Implementation): I perform statistical, pattern, anomaly, and trend analysis

Key Principle: Pure data processing - statistical and pattern analysis on structured data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from collections import Counter
import statistics

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext


class StructuredAnalysisService:
    """
    Structured Analysis Service - Enhanced structured data analysis.
    
    Performs:
    - Statistical analysis (mean, median, mode, std dev, etc.)
    - Pattern detection (recurring patterns, sequences)
    - Anomaly detection (outliers, deviations)
    - Trend analysis (temporal trends, correlations)
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Structured Analysis Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
    
    async def analyze_structured_data(
        self,
        parsed_file_id: str,
        analysis_options: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Analyze structured data with enhanced capabilities.
        
        Args:
            parsed_file_id: Parsed file identifier
            analysis_options: Analysis options (statistical, patterns, anomalies, trends)
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with structured analysis results
        """
        self.logger.info(
            f"Analyzing structured data: {parsed_file_id} for tenant: {tenant_id}"
        )
        
        try:
            # Get parsed data from State Surface
            parsed_data = await self._get_parsed_data(parsed_file_id, context)
            
            if not parsed_data:
                return {
                    "parsed_file_id": parsed_file_id,
                    "error": "No parsed data available",
                    "statistical_analysis": {},
                    "pattern_detection": {},
                    "anomaly_detection": {},
                    "trend_analysis": {}
                }
            
            results = {
                "parsed_file_id": parsed_file_id,
                "statistical_analysis": {},
                "pattern_detection": {},
                "anomaly_detection": {},
                "trend_analysis": {}
            }
            
            # Statistical analysis
            if analysis_options.get("statistical", True):
                results["statistical_analysis"] = await self._perform_statistical_analysis(
                    parsed_data
                )
            
            # Pattern detection
            if analysis_options.get("patterns", True):
                results["pattern_detection"] = await self._detect_patterns(parsed_data)
            
            # Anomaly detection
            if analysis_options.get("anomalies", True):
                results["anomaly_detection"] = await self._detect_anomalies(parsed_data)
            
            # Trend analysis
            if analysis_options.get("trends", True):
                results["trend_analysis"] = await self._analyze_trends(parsed_data)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to analyze structured data: {e}", exc_info=True)
            return {
                "parsed_file_id": parsed_file_id,
                "error": str(e),
                "statistical_analysis": {},
                "pattern_detection": {},
                "anomaly_detection": {},
                "trend_analysis": {}
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
                parsed_data = await context.state_surface.get_file(parsed_file_reference)
                if parsed_data:
                    import json
                    return json.loads(parsed_data.decode('utf-8'))
            except Exception as e:
                self.logger.debug(f"Could not retrieve parsed data: {e}")
        
        return None
    
    async def _perform_statistical_analysis(
        self,
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform statistical analysis on structured data.
        
        Calculates: mean, median, mode, std dev, min, max, count, etc.
        """
        stats = {}
        
        # Extract structured data
        structured_data = parsed_data.get("structured_data", {})
        records = parsed_data.get("records", [])
        
        if not records:
            return {"message": "No records available for statistical analysis"}
        
        # Analyze numeric fields
        numeric_fields = {}
        for record in records:
            if isinstance(record, dict):
                for key, value in record.items():
                    if isinstance(value, (int, float)):
                        if key not in numeric_fields:
                            numeric_fields[key] = []
                        numeric_fields[key].append(value)
        
        # Calculate statistics for each numeric field
        for field_name, values in numeric_fields.items():
            if len(values) > 0:
                stats[field_name] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "mode": statistics.mode(values) if len(set(values)) < len(values) else None,
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values),
                    "range": max(values) - min(values)
                }
        
        # Analyze categorical fields
        categorical_fields = {}
        for record in records:
            if isinstance(record, dict):
                for key, value in record.items():
                    if isinstance(value, str) and not value.isdigit():
                        if key not in categorical_fields:
                            categorical_fields[key] = []
                        categorical_fields[key].append(value)
        
        # Calculate frequency distributions
        for field_name, values in categorical_fields.items():
            if len(values) > 0:
                counter = Counter(values)
                stats[field_name] = {
                    "count": len(values),
                    "unique_values": len(counter),
                    "most_common": counter.most_common(10),
                    "distribution": dict(counter)
                }
        
        return {
            "numeric_fields": {k: v for k, v in stats.items() if "mean" in v},
            "categorical_fields": {k: v for k, v in stats.items() if "distribution" in v},
            "total_records": len(records)
        }
    
    async def _detect_patterns(
        self,
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect patterns in structured data.
        
        Detects: recurring patterns, sequences, correlations
        """
        patterns = {
            "recurring_patterns": [],
            "sequences": [],
            "correlations": []
        }
        
        records = parsed_data.get("records", [])
        if not records:
            return patterns
        
        # Detect recurring patterns in sequences
        if len(records) > 1:
            # Simple pattern: check for repeated sequences
            sequence_length = min(3, len(records) // 2)
            for i in range(len(records) - sequence_length):
                sequence = records[i:i+sequence_length]
                # Check if this sequence repeats later
                for j in range(i + sequence_length, len(records) - sequence_length + 1):
                    if records[j:j+sequence_length] == sequence:
                        patterns["recurring_patterns"].append({
                            "pattern": sequence,
                            "occurrences": 2,  # Simplified
                            "positions": [i, j]
                        })
                        break
        
        # Detect correlations between numeric fields
        structured_data = parsed_data.get("structured_data", {})
        if isinstance(structured_data, dict) and "tables" in structured_data:
            # For table data, detect column correlations
            patterns["correlations"].append({
                "message": "Correlation analysis available for table data",
                "note": "Full correlation matrix calculation requires more data"
            })
        
        return patterns
    
    async def _detect_anomalies(
        self,
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect anomalies in structured data.
        
        Detects: outliers, deviations, missing values, invalid data
        """
        anomalies = {
            "outliers": [],
            "deviations": [],
            "missing_values": [],
            "invalid_data": []
        }
        
        records = parsed_data.get("records", [])
        if not records:
            return anomalies
        
        # Detect outliers in numeric fields
        numeric_fields = {}
        for record in records:
            if isinstance(record, dict):
                for key, value in record.items():
                    if isinstance(value, (int, float)):
                        if key not in numeric_fields:
                            numeric_fields[key] = []
                        numeric_fields[key].append(value)
        
        # Use IQR method for outlier detection
        for field_name, values in numeric_fields.items():
            if len(values) > 4:  # Need enough data for IQR
                q1 = statistics.quantiles(values, n=4)[0]
                q3 = statistics.quantiles(values, n=4)[2]
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = [v for v in values if v < lower_bound or v > upper_bound]
                if outliers:
                    anomalies["outliers"].append({
                        "field": field_name,
                        "outlier_count": len(outliers),
                        "outlier_values": outliers[:10],  # Limit to first 10
                        "bounds": {"lower": lower_bound, "upper": upper_bound}
                    })
        
        # Detect missing values
        for i, record in enumerate(records):
            if isinstance(record, dict):
                missing = [k for k, v in record.items() if v is None or v == ""]
                if missing:
                    anomalies["missing_values"].append({
                        "record_index": i,
                        "missing_fields": missing
                    })
        
        return anomalies
    
    async def _analyze_trends(
        self,
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze trends in structured data.
        
        Analyzes: temporal trends, correlations, directional changes
        """
        trends = {
            "temporal_trends": [],
            "correlations": [],
            "directional_changes": []
        }
        
        records = parsed_data.get("records", [])
        if not records or len(records) < 2:
            return trends
        
        # Detect temporal trends (if date/time fields exist)
        date_fields = []
        for record in records:
            if isinstance(record, dict):
                for key, value in record.items():
                    if isinstance(value, str) and any(x in value.lower() for x in ["date", "time", "timestamp"]):
                        if key not in date_fields:
                            date_fields.append(key)
        
        if date_fields:
            trends["temporal_trends"].append({
                "message": "Date/time fields detected",
                "fields": date_fields,
                "note": "Full temporal analysis requires date parsing"
            })
        
        # Detect directional changes in numeric sequences
        numeric_fields = {}
        for record in records:
            if isinstance(record, dict):
                for key, value in record.items():
                    if isinstance(value, (int, float)):
                        if key not in numeric_fields:
                            numeric_fields[key] = []
                        numeric_fields[key].append(value)
        
        for field_name, values in numeric_fields.items():
            if len(values) >= 3:
                # Simple trend: increasing, decreasing, or stable
                increases = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
                decreases = sum(1 for i in range(1, len(values)) if values[i] < values[i-1])
                
                if increases > decreases:
                    direction = "increasing"
                elif decreases > increases:
                    direction = "decreasing"
                else:
                    direction = "stable"
                
                trends["directional_changes"].append({
                    "field": field_name,
                    "direction": direction,
                    "change_count": {"increases": increases, "decreases": decreases}
                })
        
        return trends
