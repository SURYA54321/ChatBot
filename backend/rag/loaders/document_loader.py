import logging
import os
from io import BytesIO
from pathlib import Path
from typing import List

import pymupdf
import pytesseract
from PIL import Image
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
)

logger = logging.getLogger(__name__)


# Tesseract executable
TESSERACT_CMD = os.getenv(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# OCR settings
OCR_MIN_TEXT_LENGTH = 20
OCR_DPI = 200


def _has_usable_text(text: str) -> bool:
    """
    Checks whether the PDF page contains enough real text
    to avoid unnecessary OCR.
    """
    if not text:
        return False

    cleaned = " ".join(text.split())

    if len(cleaned) < OCR_MIN_TEXT_LENGTH:
        return False

    return any(character.isalnum() for character in cleaned)


def _ocr_page(page) -> str:
    """
    Render a PDF page as an image and extract text using Tesseract.
    """
    matrix = pymupdf.Matrix(
        OCR_DPI / 72,
        OCR_DPI / 72,
    )

    pixmap = page.get_pixmap(
        matrix=matrix,
        alpha=False,
    )

    image_bytes = pixmap.tobytes("png")
    image = Image.open(BytesIO(image_bytes))

    text = pytesseract.image_to_string(
        image,
        config="--psm 6",
    )

    return text.strip()


def _load_pdf_with_ocr(path: Path) -> List[Document]:
    """
    Loads a PDF page by page.

    1. Try normal PDF text extraction.
    2. If the page has little/no usable text, use OCR.
    3. Return LangChain Documents so the existing
       splitter and ingestion pipeline can remain unchanged.
    """

    pdf = pymupdf.open(str(path))
    documents = []

    try:
        for page_index, page in enumerate(pdf):

            # First try normal PDF text extraction
            native_text = page.get_text("text").strip()

            if _has_usable_text(native_text):
                text = native_text
                extraction_method = "native"

                logger.info(
                    "Page %d of %s extracted using native PDF text.",
                    page_index + 1,
                    path.name,
                )

            else:
                # No usable text → OCR
                logger.info(
                    "Page %d of %s has no usable native text. "
                    "Running OCR.",
                    page_index + 1,
                    path.name,
                )

                text = _ocr_page(page)
                extraction_method = "ocr"

            # Skip completely empty pages
            if not text:
                logger.warning(
                    "No text extracted from page %d of %s.",
                    page_index + 1,
                    path.name,
                )
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": str(path),
                        "page": page_index,
                        "page_number": page_index + 1,
                        "extraction_method": extraction_method,
                    },
                )
            )

    finally:
        pdf.close()

    return documents


def load_document(file_path: str):
    """
    Loads documents into LangChain Document format.

    PDFs use native text extraction first and automatically
    fall back to OCR for image/scanned pages.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = path.suffix.lower()

    if extension == ".pdf":
        return _load_pdf_with_ocr(path)

    elif extension == ".docx":
        loader = Docx2txtLoader(str(path))

    elif extension == ".txt":
        loader = TextLoader(
            str(path),
            encoding="utf-8",
        )

    elif extension == ".csv":
        loader = CSVLoader(str(path))

    else:
        raise ValueError(
            f"Unsupported file format: '{extension}'"
        )

    return loader.load()