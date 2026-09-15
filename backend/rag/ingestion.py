import logging
from typing import List
from django.db import transaction

from documents.models import DocumentChunk
from rag.loaders.document_loader import load_document
from rag.embeddings.embedding_model import get_embedding_model

# New to version-5
# Handles both import path structures safely
try:
    from rag.loaders.text_splitter import split_documents
except ImportError:
    from rag.splitters.text_splitter import split_documents

logger = logging.getLogger(__name__)


def process_document(
    file_path: str,
    user_id: str,
    conversation_id: str,
    document_id: str,
    filename: str,
    file_type: str,
) -> List:
    """
    Load, split, generate remote embeddings via Hugging Face API, 
    and store document chunks directly into SQLite for lightweight RAG.
    """
    try:
        # Step 1: Load file content using lightweight parsers (PyMuPDF / Docx2txt)
        documents = load_document(file_path)
        if not documents:
            logger.warning(f"No content extracted from file: {file_path}")
            return []

        # Step 2: Split content into text chunks
        chunks = split_documents(documents)
        if not chunks:
            logger.warning(f"No chunks generated for file: {file_path}")
            return []

        # Step 3: Enrich chunk metadata and extract raw texts
        chunk_texts = []
        for index, chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    "user_id": str(user_id),
                    "conversation_id": str(conversation_id),
                    "document_id": str(document_id),
                    "filename": filename,
                    "file_type": file_type,
                    "chunk_index": index,
                    "source": filename,
                }
            )
            chunk_texts.append(chunk.page_content)

        # Step 4: Generate vector embeddings remotely via HF API (0 MB local PyTorch RAM)
        embedding_model = get_embedding_model()
        embeddings = embedding_model.embed_documents(chunk_texts)

        # Step 5: Save chunks atomically to SQLite DocumentChunk table
        with transaction.atomic():
            # Remove pre-existing chunks for this document if re-ingesting
            DocumentChunk.objects.filter(document_id=document_id).delete()

            db_chunks = []
            for index, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                page_num = chunk.metadata.get("page", None)

                db_chunk = DocumentChunk(
                    document_id=document_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    chunk_index=index,
                    content=chunk.page_content,
                    embedding=vector,  # Native Python float list saved directly into JSONField
                    filename=filename,
                    file_type=file_type,
                    page=page_num if isinstance(page_num, int) else None,
                )
                db_chunks.append(db_chunk)

            DocumentChunk.objects.bulk_create(db_chunks)

        logger.info(
            f"Successfully ingested {len(db_chunks)} chunks into SQLite for document {document_id}."
        )
        return chunks

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        raise e