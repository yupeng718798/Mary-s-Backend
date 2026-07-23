import os
from pathlib import Path


def extract_text_from_pdf(file_path: str) -> str:
    """从 PDF 文件提取文本"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        text = "\n".join(text_parts).strip()
        return text if text else ""
    except Exception as e:
        return f"[PDF提取失败: {str(e)}]"


def extract_text_from_image(file_path: str) -> str:
    """从图片提取文本（OCR）"""
    try:
        from PIL import Image
        import pytesseract
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang="chi_sim+eng")
        return text.strip() if text else ""
    except Exception as e:
        return f"[图片OCR失败: {str(e)}]"


def extract_text(file_path: str) -> str:
    """根据文件类型自动提取文本"""
    if not file_path or not os.path.exists(file_path):
        return "[文件不存在]"

    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"):
        return extract_text_from_image(file_path)
    else:
        return f"[不支持的文件类型: {ext}]"
