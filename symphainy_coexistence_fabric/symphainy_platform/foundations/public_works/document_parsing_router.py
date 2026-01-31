"""
Unified document parsing surface (P4).

Single entry point that implements FileParsingProtocol and routes by parsing_type
and file_type to the appropriate processing abstraction. Callers use
get_document_parsing() and call parse_file(request) only; no format-specific get_*.

Supported formats (declared capabilities): PDF, Word, Excel, CSV, JSON, text, HTML,
image (PNG/JPEG/TIFF with OCR where supported), mainframe (copybook-based), Kreuzberg (PDF),
data_model (JSON Schema / YAML), workflow (BPMN/DrawIO), SOP (Markdown). Limits per format
are documented in docs/ or at the parsing entry point.
"""

from typing import Any, Dict, Optional

from .protocols.file_parsing_protocol import (
    FileParsingProtocol,
    FileParsingRequest,
    FileParsingResult,
)


def _file_type_from_filename(filename: str) -> str:
    """Derive file_type (extension) from filename."""
    if not filename or "." not in filename:
        return "text"
    return filename.rsplit(".", 1)[-1].lower()


class DocumentParsingRouter:
    """
    Routes parse_file(request) to the correct processing abstraction by
    parsing_type and file_type. Implements FileParsingProtocol.
    """

    def __init__(self, public_works: Any):
        """
        Args:
            public_works: PublicWorksFoundationService (or any object exposing get_*_processing_abstraction).
        """
        self._pw = public_works

    def _get_parser(
        self,
        parsing_type: str,
        file_type: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Return the processing abstraction for the given parsing_type and file_type."""
        opts = options or {}
        if parsing_type == "unstructured":
            if file_type in ["pdf"]:
                if opts.get("use_kreuzberg"):
                    return self._pw.get_kreuzberg_processing_abstraction()
                return self._pw.get_pdf_processing_abstraction()
            if file_type in ["docx", "doc"]:
                return self._pw.get_word_processing_abstraction()
            if file_type in ["txt", "text"]:
                return self._pw.get_text_processing_abstraction()
            if file_type in ["html", "htm"]:
                return self._pw.get_html_processing_abstraction()
            if file_type in ["png", "jpg", "jpeg", "gif", "bmp", "tiff"]:
                return self._pw.get_image_processing_abstraction()
            return self._pw.get_text_processing_abstraction()
        if parsing_type == "structured":
            if file_type in ["xlsx", "xls"]:
                return self._pw.get_excel_processing_abstraction()
            if file_type in ["csv"]:
                return self._pw.get_csv_processing_abstraction()
            if file_type in ["json"]:
                return self._pw.get_json_processing_abstraction()
            if file_type in ["bin", "binary"]:
                return self._pw.get_mainframe_processing_abstraction()
            return self._pw.get_csv_processing_abstraction()
        if parsing_type == "hybrid":
            if file_type in ["pdf"]:
                if opts.get("use_kreuzberg"):
                    return self._pw.get_kreuzberg_processing_abstraction()
                return self._pw.get_pdf_processing_abstraction()
            return self._pw.get_excel_processing_abstraction()
        if parsing_type == "workflow":
            if file_type in ["json"]:
                return self._pw.get_json_processing_abstraction()
            return self._pw.get_text_processing_abstraction()
        if parsing_type == "sop":
            return self._pw.get_text_processing_abstraction()
        if parsing_type == "data_model":
            ab = self._pw.get_data_model_processing_abstraction()
            if ab:
                return ab
            if file_type in ["json"]:
                return self._pw.get_json_processing_abstraction()
            return self._pw.get_text_processing_abstraction()
        return self._pw.get_text_processing_abstraction()

    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Route to the appropriate parser and return FileParsingResult.
        parsing_type and file_type are taken from request.options or derived from request.filename.
        """
        opts = request.options or {}
        parsing_type = opts.get("parsing_type")
        file_type = opts.get("file_type") or _file_type_from_filename(request.filename or "")
        if not parsing_type:
            parsing_type = self._infer_parsing_type(
                file_type=file_type,
                filename=request.filename or "",
                options=opts,
            )
        parser = self._get_parser(parsing_type, file_type, opts)
        if not parser:
            return FileParsingResult(
                success=False,
                error="No parser available for parsing_type=%s file_type=%s" % (parsing_type, file_type),
                parsing_type=parsing_type,
            )
        return await parser.parse_file(request)

    def _infer_parsing_type(
        self,
        file_type: str,
        filename: str,
        options: Dict[str, Any],
    ) -> str:
        """Infer parsing_type from file_type, filename, and options (mirrors FileParserService logic)."""
        if options.get("parsing_type"):
            return options["parsing_type"]
        if options.get("is_workflow"):
            return "workflow"
        if options.get("is_sop"):
            return "sop"
        if options.get("is_data_model") or options.get("data_model"):
            return "data_model"
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        structured = ["xlsx", "xls", "csv", "bin", "binary"]
        unstructured = ["pdf", "docx", "doc", "txt", "text", "html", "htm"]
        if file_type == "data_model" or options.get("is_data_model"):
            return "data_model"
        if ext in ["bpmn", "drawio"]:
            return "workflow"
        if ext in ["md", "markdown"]:
            return "sop"
        if ext in structured or file_type in structured:
            return "structured"
        if ext in unstructured or file_type in unstructured:
            return "unstructured"
        if ext == "json" and options.get("is_workflow"):
            return "workflow"
        return "unstructured"
