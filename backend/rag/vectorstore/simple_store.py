import numpy as np

from langchain_core.documents import Document as LCDocument

from documents.models import DocumentChunk
from rag.embeddings.embedding_model import get_embedding_model


def add_documents(chunks):
    """
    Embed all chunks in ONE batched remote API call (not one call
    per chunk), then bulk-insert into the database.
    """
    if not chunks:
        return []

    embedding_model = get_embedding_model()
    texts = [chunk.page_content for chunk in chunks]
    vectors = embedding_model.embed_documents(texts)

    objects = []

    for chunk, vector in zip(chunks, vectors):
        metadata = chunk.metadata

        objects.append(
            DocumentChunk(
                document_id=metadata["document_id"],
                user_id=metadata["user_id"],
                conversation_id=metadata["conversation_id"],
                chunk_index=metadata.get("chunk_index", 0),
                content=chunk.page_content,
                embedding=vector,
                filename=metadata.get("filename", ""),
                file_type=metadata.get("file_type", ""),
                page=metadata.get("page"),
            )
        )

    DocumentChunk.objects.bulk_create(objects)

    return [str(obj.id) for obj in objects]


def similarity_search_with_relevance_scores(query, user_id, conversation_id, k=5):
    """
    Plain cosine similarity over this conversation's chunks.
    """
    embedding_model = get_embedding_model()
    query_vector = np.array(embedding_model.embed_query(query), dtype=np.float32)
    query_norm = np.linalg.norm(query_vector)

    if query_norm == 0:
        return []

    chunks = DocumentChunk.objects.filter(
        user_id=user_id,
        conversation_id=conversation_id,
    )

    scored = []

    for chunk in chunks:
        vector = np.array(chunk.embedding, dtype=np.float32)
        vector_norm = np.linalg.norm(vector)

        if vector_norm == 0:
            continue

        score = float(np.dot(query_vector, vector) / (query_norm * vector_norm))

        lc_document = LCDocument(
            page_content=chunk.content,
            metadata={
                "document_id": str(chunk.document_id),
                "filename": chunk.filename,
                "file_type": chunk.file_type,
                "page": chunk.page,
                "chunk_index": chunk.chunk_index,
            },
        )

        scored.append((lc_document, score))

    scored.sort(key=lambda pair: pair[1], reverse=True)

    return scored[:k]


def get_document_order_chunks(user_id, conversation_id, limit=5):
    """
    For summary/overview requests. Returns chunks in document order
    (not similarity-ranked) so a summarization request gets broad
    coverage across the document rather than a narrow topical match.
    """
    chunks = DocumentChunk.objects.filter(
        user_id=user_id,
        conversation_id=conversation_id,
    ).order_by("document_id", "chunk_index")[:limit]

    documents = []

    for chunk in chunks:
        documents.append(
            LCDocument(
                page_content=chunk.content,
                metadata={
                    "document_id": str(chunk.document_id),
                    "filename": chunk.filename,
                    "file_type": chunk.file_type,
                    "page": chunk.page,
                    "chunk_index": chunk.chunk_index,
                },
            )
        )

    return documents


def delete_document_vectors(document_id, user_id):
    DocumentChunk.objects.filter(document_id=document_id, user_id=user_id).delete()