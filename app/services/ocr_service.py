"""
OCR Service - Uses PaddleOCR to extract text from medical images
First version supports image formats: .jpg, .jpeg, .png
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from image using PaddleOCR
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Extracted text content
    """
    try:
        from paddleocr import PaddleOCR
        
        # Initialize PaddleOCR
        # use_angle_cls=True enables rotated text recognition
        # lang='ch' supports Chinese + English mixed text
        ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            show_log=False  # Don't show detailed logs
        )
        
        # Run OCR recognition
        result = ocr.ocr(file_path, cls=True)
        
        # Extract text
        text_parts = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    text_parts.append(line[1][0])  # Extract recognized text
        
        extracted_text = "\n".join(text_parts).strip()
        
        if extracted_text:
            logger.info(f"OCR extraction succeeded, extracted {len(extracted_text)} characters")
            return extracted_text
        else:
            logger.warning("OCR did not recognize any text")
            return ""
            
    except ImportError as e:
        error_msg = f"PaddleOCR not installed: {str(e)}"
        logger.error(error_msg)
        return f"[OCR service unavailable: {error_msg}]"
        
    except Exception as e:
        error_msg = f"OCR recognition failed: {str(e)}"
        logger.error(error_msg)
        return f"[{error_msg}]"


def extract_text(file_path: str, file_type: Optional[str] = None) -> str:
    """
    Extract text based on file type
    
    First version supports image formats only:
    - .jpg, .jpeg, .png
    
    Args:
        file_path: Path to the file
        file_type: File type (optional, for validation)
        
    Returns:
        Extracted text content
    """
    if not file_path or not os.path.exists(file_path):
        return "[File not found]"
    
    # Get file extension
    ext = Path(file_path).suffix.lower()
    
    # Only support image formats
    supported_image_formats = {'.jpg', '.jpeg', '.png'}
    
    if ext not in supported_image_formats:
        return f"[Unsupported file type: {ext}, currently only supports image formats: .jpg, .jpeg, .png]"
    
    # Run OCR
    return extract_text_from_image(file_path)