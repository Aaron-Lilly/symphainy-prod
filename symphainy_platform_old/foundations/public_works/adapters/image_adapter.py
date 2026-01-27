"""
Image Processing Adapter - Layer 0

Raw technology client for image OCR (Optical Character Recognition).
Uses pytesseract or similar for OCR.

WHAT (Infrastructure): I provide image OCR capabilities
HOW (Adapter): I use pytesseract to extract text from images
"""

import logging
from typing import Dict, Any, Optional
import io

logger = logging.getLogger(__name__)


class ImageProcessingAdapter:
    """
    Adapter for image OCR processing.
    
    Uses pytesseract for OCR extraction from images.
    """
    
    def __init__(self):
        """Initialize Image Processing Adapter."""
        self.logger = logger
        self.pytesseract_available = False
        self.pil_available = False
        
        # Try to import pytesseract
        try:
            import pytesseract
            self.pytesseract = pytesseract
            self.pytesseract_available = True
            self.logger.info("✅ Pytesseract available for OCR")
        except ImportError:
            self.logger.warning("⚠️ Pytesseract not available - OCR will not work")
        
        # Try to import PIL/Pillow (required for image processing)
        try:
            from PIL import Image
            self.Image = Image
            self.pil_available = True
            self.logger.info("✅ PIL/Pillow available for image processing")
        except ImportError:
            self.logger.warning("⚠️ PIL/Pillow not available - OCR will not work")
        
        if not self.pytesseract_available or not self.pil_available:
            self.logger.warning("⚠️ OCR dependencies not fully available - image parsing will be limited")
        
        self.logger.info("✅ Image Processing Adapter initialized")
    
    async def extract_text_from_bytes(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract text from image using OCR.
        
        Args:
            image_data: Image file content as bytes
        
        Returns:
            Dict with extracted text:
            {
                "success": bool,
                "text": str,  # Extracted text
                "metadata": Dict,
                "error": Optional[str]
            }
        """
        try:
            if not self.pytesseract_available or not self.pil_available:
                return {
                    "success": False,
                    "error": "OCR dependencies (pytesseract/PIL) not available",
                    "text": "",
                    "metadata": {}
                }
            
            # Open image from bytes
            image = self.Image.open(io.BytesIO(image_data))
            
            # Extract text using OCR
            extracted_text = self.pytesseract.image_to_string(image)
            
            # Get image metadata
            width, height = image.size
            format_name = image.format or "unknown"
            
            metadata = {
                "type": "image",
                "format": format_name,
                "width": width,
                "height": height,
                "size": len(image_data)
            }
            
            return {
                "success": True,
                "text": extracted_text,
                "metadata": metadata
            }
        
        except Exception as e:
            self.logger.error(f"❌ OCR extraction failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"OCR extraction failed: {str(e)}",
                "text": "",
                "metadata": {}
            }
