"""
OCR Service - Extracts text from medical images.
Currently uses a lightweight fallback; PaddleOCR can be enabled
by installing paddlepaddle and paddleocr manually.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from image. Returns extracted text or a status message.
    """
    try:
        # Try PaddleOCR if available (optional dependency)
        from paddleocr import PaddleOCR

        ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            show_log=False
        )

        result = ocr.ocr(file_path, cls=True)

        text_parts = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    text_parts.append(line[1][0])

        extracted_text = "\n".join(text_parts).strip()

        if extracted_text:
            logger.info(f"OCR extraction succeeded, extracted {len(extracted_text)} characters")
            return extracted_text
        else:
            logger.warning("OCR did not recognize any text")
            return ""

    except ImportError:
        logger.info("PaddleOCR not installed, using basic file info extraction")
        file_name = Path(file_path).name
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        return (
            f"[Image file: {file_name}]\n"
            f"[Size: {file_size} bytes]\n"
            f"[OCR is not available in this environment. "
            f"The image has been saved and can be analyzed manually.]"
        )

    except Exception as e:
        error_msg = f"OCR recognition failed: {str(e)}"
        logger.error(error_msg)
        return f"[{error_msg}]"


def extract_text(file_path: str, file_type: Optional[str] = None) -> str:
    """
    Extract text based on file type.

    Supported image formats: .jpg, .jpeg, .png
    """
    if not file_path or not os.path.exists(file_path):
        return "[File not found]"

    ext = Path(file_path).suffix.lower()

    supported_image_formats = {'.jpg', '.jpeg', '.png'}

    if ext not in supported_image_formats:
        return f"[Unsupported file type: {ext}, currently only supports image formats: .jpg, .jpeg, .png]"

    return extract_text_from_image(file_path)