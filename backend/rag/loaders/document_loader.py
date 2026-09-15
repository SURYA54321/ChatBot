import os
from pathlib import Path
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
)


def load_document(file_path: str):
    """
    Loads document content into LangChain Document format.
    Uses lightweight parsers (PyMuPDF, Docx2txt) to keep memory footprint 
    under Render's 512 MB Free Tier RAM limit.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = path.suffix.lower()

    if extension == ".pdf":
        loader = PyMuPDFLoader(str(path))
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