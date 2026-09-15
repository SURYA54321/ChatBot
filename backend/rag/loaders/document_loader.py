# Claude
import base64
import io
from pathlib import Path
import logging

import fitz  # PyMuPDF
from PIL import Image
from groq import Groq
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
)
from langchain_core.documents import Document

logger = logging.getLogger(__name__)
groq_client = Groq()  # reads GROQ_API_KEY from env


def _image_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _ocr_page_with_groq(img: Image.Image) -> str:
    """Send a rendered PDF page image to Groq's vision model for OCR."""
    b64_image = _image_to_base64(img)
    response = groq_client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract all readable text from this image exactly "
                            "as it appears. Return only the extracted text, no "
                            "commentary."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_image}"
                        },
                    },
                ],
            }
        ],
        temperature=0,
        max_tokens=2048,
    )
    return response.choices[0].message.content or ""


def _ocr_pdf_with_groq(path: Path):
    """Fallback: rasterize each page with PyMuPDF and OCR it via Groq's vision model."""
    docs = []
    pdf = fitz.open(str(path))
    for page_num, page in enumerate(pdf):
        pix = page.get_pixmap(dpi=200)  # good balance of accuracy vs token cost
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        logger.info(f"OCR output for page {page_num} ({len(text)} chars): {text[:200]!r}")
        text = _ocr_page_with_groq(img)
        if text.strip():
            docs.append(Document(page_content=text, metadata={"page": page_num}))
    pdf.close()
    return docs


def load_document(file_path: str):
    """
    Loads document content into LangChain Document format.
    Uses lightweight parsers (PyMuPDF, Docx2txt) to keep memory footprint
    under Render's 512 MB Free Tier RAM limit.

    For PDFs with no extractable text layer (scanned / screenshot-based),
    falls back to OCR via Groq's hosted vision model instead of a local
    OCR engine, keeping local RAM usage at ~0 MB.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = path.suffix.lower()

    if extension == ".pdf":
        loader = PyMuPDFLoader(str(path))
        documents = loader.load()

        has_text = any(doc.page_content.strip() for doc in documents)
        if not has_text:
            documents = _ocr_pdf_with_groq(path)

        return documents

    elif extension == ".docx":
        # Docx2txtLoader uses ~5MB RAM instead of Unstructured's ~250MB
        loader = Docx2txtLoader(str(path))
    elif extension == ".txt":
        loader = TextLoader(str(path), encoding="utf-8")
    elif extension == ".csv":
        loader = CSVLoader(str(path))
    else:
        raise ValueError(f"Unsupported file format: '{extension}'")

    return loader.load()

# import os
# from pathlib import Path
# from langchain_community.document_loaders import (
#     PyMuPDFLoader,
#     TextLoader,
#     CSVLoader,
#     Docx2txtLoader,
# )


# def load_document(file_path: str):
#     """
#     Loads document content into LangChain Document format.
#     Uses lightweight parsers (PyMuPDF, Docx2txt) to keep memory footprint 
#     under Render's 512 MB Free Tier RAM limit.
#     """
#     path = Path(file_path)

#     if not path.exists():
#         raise FileNotFoundError(f"File not found: {file_path}")

#     extension = path.suffix.lower()

#     if extension == ".pdf":
#         loader = PyMuPDFLoader(str(path))
#     elif extension == ".docx":
#         # Docx2txtLoader uses ~5MB RAM instead of Unstructured's ~250MB
#         loader = Docx2txtLoader(str(path))
#     elif extension == ".txt":
#         loader = TextLoader(str(path), encoding="utf-8")
#     elif extension == ".csv":
#         loader = CSVLoader(str(path))
#     else:
#         raise ValueError(f"Unsupported file format: '{extension}'")

#     return loader.load()