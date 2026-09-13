def get_document_order_chunks(user_id, conversation_id, limit=5):
    """
    >>> NEW: for summary/overview requests. Returns chunks in
    document order (not similarity-ranked) so a summarization
    request gets broad coverage across the document rather than a
    narrow topical match.
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