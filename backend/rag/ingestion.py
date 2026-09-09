from rag.loaders.document_loader import load_document
from rag.splitters.text_splitter import split_documents


def process_document(
    file_path: str,
    user_id: str,
    document_id: str,
    filename: str,
    file_type: str,
):
    """
    Load, split, and enrich a document with RAG metadata.
    """

    documents = load_document(file_path)

    chunks = split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata.update(
            {
                "user_id": str(user_id),
                "document_id": str(document_id),
                "filename": filename,
                "file_type": file_type,
                "chunk_index": index,
                "source": filename,
            }
        )

    return chunks
