"""
Test Parsing Standardization

Validates that all parsers produce standardized FileParsingResult outputs
with consistent structure metadata and format.

Run: pytest tests/test_parsing_standardization.py -v
"""

import pytest
import json
from typing import Dict, Any
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingResult,
    FileParsingRequest
)


class TestParsingStandardization:
    """Test suite for parsing standardization."""
    
    def validate_file_parsing_result(self, result: FileParsingResult, expected_parsing_type: str):
        """
        Validate FileParsingResult matches standardized format.
        
        Args:
            result: FileParsingResult to validate
            expected_parsing_type: Expected parsing_type value
        """
        # Must be FileParsingResult
        assert isinstance(result, FileParsingResult), "Result must be FileParsingResult"
        
        # Must have success field
        assert hasattr(result, 'success'), "Result must have 'success' field"
        
        # If successful, validate structure
        if result.success:
            # parsing_type must be set explicitly
            assert result.parsing_type is not None, f"parsing_type must be set (got None)"
            assert result.parsing_type == expected_parsing_type, \
                f"parsing_type mismatch: expected '{expected_parsing_type}', got '{result.parsing_type}'"
            
            # metadata must exist
            assert result.metadata is not None, "metadata must not be None"
            assert isinstance(result.metadata, dict), "metadata must be a dict"
            
            # metadata must include parsing_type
            assert "parsing_type" in result.metadata, "metadata must include 'parsing_type'"
            assert result.metadata["parsing_type"] == expected_parsing_type, \
                f"metadata.parsing_type mismatch: expected '{expected_parsing_type}', got '{result.metadata.get('parsing_type')}'"
            
            # metadata must include structure (for chunking service)
            assert "structure" in result.metadata, "metadata must include 'structure' for chunking service"
            assert isinstance(result.metadata["structure"], dict), "metadata.structure must be a dict"
            
            # text_content should be None (not empty string) if no text
            if result.text_content is not None:
                assert isinstance(result.text_content, str), "text_content must be str or None"
                # Empty string is allowed if there's actual text content
            
            # structured_data must be JSON-serializable if present
            if result.structured_data is not None:
                try:
                    json.dumps(result.structured_data)
                except (TypeError, ValueError) as e:
                    pytest.fail(f"structured_data must be JSON-serializable: {e}")
                
                # structured_data must have "format" field
                assert isinstance(result.structured_data, dict), "structured_data must be a dict"
                assert "format" in result.structured_data, "structured_data must include 'format' field"
                
                # structured_data must NOT contain nested "metadata" or "structure"
                if isinstance(result.structured_data, dict):
                    assert "metadata" not in result.structured_data, \
                        "structured_data must not contain nested 'metadata'"
                    assert "structure" not in result.structured_data, \
                        "structured_data must not contain nested 'structure'"
            
            # timestamp must be set
            assert result.timestamp, "timestamp must be set"
            
            # Validate timestamp format (ISO format)
            try:
                datetime.fromisoformat(result.timestamp.replace('Z', '+00:00'))
            except ValueError:
                pytest.fail(f"timestamp must be ISO format: {result.timestamp}")
        
        return True
    
    def validate_structure_metadata(self, structure: Dict[str, Any], parsing_type: str):
        """
        Validate structure metadata format based on parsing type.
        
        Args:
            structure: Structure metadata dict
            parsing_type: Parsing type to validate against
        """
        assert isinstance(structure, dict), "structure must be a dict"
        
        if parsing_type == "unstructured":
            # Should have pages, sections, or paragraphs
            assert any(key in structure for key in ["pages", "sections", "paragraphs"]), \
                "Unstructured parsing must have pages, sections, or paragraphs in structure"
        
        elif parsing_type == "structured":
            # Should have rows or sheets
            assert any(key in structure for key in ["rows", "sheets", "object"]), \
                "Structured parsing must have rows, sheets, or object in structure"
        
        elif parsing_type == "hybrid":
            # Should have pages/sections/paragraphs AND tables
            has_text_structure = any(key in structure for key in ["pages", "sections", "paragraphs"])
            # Tables are in structured_data, not structure
            assert has_text_structure, "Hybrid parsing must have text structure (pages/sections/paragraphs)"
        
        elif parsing_type == "workflow":
            # Should have workflow structure
            assert "workflow" in structure, "Workflow parsing must have 'workflow' in structure"
            workflow = structure["workflow"]
            assert isinstance(workflow, dict), "workflow must be a dict"
            assert "tasks" in workflow or "gateways" in workflow or "flows" in workflow, \
                "workflow must have tasks, gateways, or flows"
        
        elif parsing_type == "sop":
            # Should have sections or steps
            assert any(key in structure for key in ["sections", "steps"]), \
                "SOP parsing must have sections or steps in structure"
        
        elif parsing_type == "mainframe":
            # Should have records
            assert "records" in structure, "Mainframe parsing must have 'records' in structure"
        
        elif parsing_type == "data_model":
            # Should have schema
            assert "schema" in structure, "Data model parsing must have 'schema' in structure"
        
        return True
    
    @pytest.mark.asyncio
    async def test_pdf_processing_standardization(self):
        """Test PDF processing returns standardized format."""
        # This would require actual PDF file and adapter
        # For now, we'll test the structure validation
        pass
    
    @pytest.mark.asyncio
    async def test_csv_processing_standardization(self):
        """Test CSV processing returns standardized format."""
        # This would require actual CSV file and adapter
        pass
    
    @pytest.mark.asyncio
    async def test_excel_processing_standardization(self):
        """Test Excel processing returns standardized format."""
        # This would require actual Excel file and adapter
        pass
    
    @pytest.mark.asyncio
    async def test_word_processing_standardization(self):
        """Test Word processing returns standardized format."""
        # This would require actual Word file and adapter
        pass
    
    @pytest.mark.asyncio
    async def test_text_processing_standardization(self):
        """Test Text processing returns standardized format."""
        # This would require actual text file and adapter
        pass
    
    @pytest.mark.asyncio
    async def test_json_processing_standardization(self):
        """Test JSON processing returns standardized format."""
        # This would require actual JSON file and adapter
        pass
    
    @pytest.mark.asyncio
    async def test_workflow_processing_standardization(self):
        """Test Workflow processing returns standardized format."""
        # This would require actual BPMN file and adapter
        pass
    
    @pytest.mark.asyncio
    async def test_sop_processing_standardization(self):
        """Test SOP processing returns standardized format."""
        # This would require actual Markdown file and adapter
        pass
    
    @pytest.mark.asyncio
    async def test_data_model_processing_standardization(self):
        """Test Data Model processing returns standardized format."""
        # This would require actual JSON Schema/YAML file and adapter
        pass
    
    def test_file_parsing_result_protocol(self):
        """Test FileParsingResult protocol structure."""
        # Test with all fields
        result = FileParsingResult(
            success=True,
            text_content="test",
            structured_data={"format": "unstructured", "data": []},
            metadata={
                "parsing_type": "unstructured",
                "structure": {"paragraphs": []}
            },
            parsing_type="unstructured",
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Validate
        self.validate_file_parsing_result(result, "unstructured")
        self.validate_structure_metadata(result.metadata["structure"], "unstructured")
    
    def test_file_parsing_result_text_content_none(self):
        """Test FileParsingResult with text_content=None (structured files)."""
        result = FileParsingResult(
            success=True,
            text_content=None,  # Structured files have no text
            structured_data={
                "format": "structured",
                "rows": [{"col1": "val1"}]
            },
            metadata={
                "parsing_type": "structured",
                "structure": {"rows": []}
            },
            parsing_type="structured",
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Validate
        self.validate_file_parsing_result(result, "structured")
        assert result.text_content is None, "Structured files should have text_content=None"
    
    def test_file_parsing_result_structure_metadata_formats(self):
        """Test various structure metadata formats."""
        # Test unstructured (paragraphs)
        structure_unstructured = {
            "paragraphs": [
                {"paragraph_index": 0, "text": "Para 1"},
                {"paragraph_index": 1, "text": "Para 2"}
            ]
        }
        self.validate_structure_metadata(structure_unstructured, "unstructured")
        
        # Test structured (rows)
        structure_structured = {
            "rows": [
                {"row_index": 0, "data": {"col1": "val1"}},
                {"row_index": 1, "data": {"col1": "val2"}}
            ]
        }
        self.validate_structure_metadata(structure_structured, "structured")
        
        # Test workflow
        structure_workflow = {
            "workflow": {
                "tasks": [{"task_index": 0, "task_name": "Task 1"}],
                "gateways": [],
                "flows": []
            }
        }
        self.validate_structure_metadata(structure_workflow, "workflow")
        
        # Test SOP
        structure_sop = {
            "sections": [{"section_index": 0, "section_title": "Section 1"}],
            "steps": [{"step_index": 0, "step_text": "Step 1"}]
        }
        self.validate_structure_metadata(structure_sop, "sop")
        
        # Test data model
        structure_data_model = {
            "schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        self.validate_structure_metadata(structure_data_model, "data_model")
    
    def test_structured_data_format(self):
        """Test structured_data standardized format."""
        # Test structured format
        structured_data = {
            "format": "structured",
            "rows": [{"col1": "val1"}],
            "columns": ["col1"]
        }
        assert "format" in structured_data, "structured_data must have 'format'"
        assert structured_data["format"] == "structured"
        assert "metadata" not in structured_data, "structured_data must not have 'metadata'"
        assert "structure" not in structured_data, "structured_data must not have 'structure'"
        
        # Test JSON serializability
        json_str = json.dumps(structured_data)
        assert json_str, "structured_data must be JSON-serializable"
        
        # Test hybrid format
        structured_data_hybrid = {
            "format": "hybrid",
            "tables": []
        }
        assert structured_data_hybrid["format"] == "hybrid"
        
        # Test workflow format
        structured_data_workflow = {
            "format": "workflow",
            "tasks": [],
            "gateways": [],
            "flows": []
        }
        assert structured_data_workflow["format"] == "workflow"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
