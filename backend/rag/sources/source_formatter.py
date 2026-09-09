def format_sources(documents):
    """
    Convert retrieved LangChain documents into
    clean, deduplicated source metadata.
    """

    sources = []
    seen = set()

    for document in documents:
        metadata = document.metadata

        document_id = metadata.get("document_id")
        filename = metadata.get(
            "filename",
            "Unknown",
        )
        file_type = metadata.get("file_type")
        page = metadata.get("page")
        chunk_index = metadata.get("chunk_index")

        # PyMuPDF pages are zero-indexed.
        if page is not None:
            page = page + 1

        source_key = (
            str(document_id),
            page,
        )

        if source_key in seen:
            continue

        seen.add(source_key)

        sources.append(
            {
                "document_id": document_id,
                "filename": filename,
                "file_type": file_type,
                "page": page,
                "chunk_index": chunk_index,
            }
        )

    return sources
