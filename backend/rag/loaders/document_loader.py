from pathlib import Path

from langchain_community.document_loaders import (
    CSVLoader,
    PyMuPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)


def load_document(file_path: str):
    """
    Load a document based on its file extension.

    Returns:
        list[Document]
    """

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        loader = PyMuPDFLoader(str(path))

    elif extension in {".txt", ".md"}:
        loader = TextLoader(
            str(path),
            encoding="utf-8",
        )

    elif extension == ".docx":
        loader = UnstructuredWordDocumentLoader(
            str(path)
        )

    elif extension == ".csv":
        loader = CSVLoader(str(path))

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    return loader.load()
