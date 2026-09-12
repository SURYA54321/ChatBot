from rag.retrievers.query_rewriter import rewrite_query
from rag.vectorstore.chroma_store import get_vector_store


def retrieve_documents(
    question: str,
    user_id: str,
    conversation_id: str,
    chat_history: str = "",
    final_k: int = 5,
):
    rewritten_query = rewrite_query(
        question=question,
        chat_history=chat_history,
    )

    vector_store = get_vector_store()

    # >>> FIXED: method name typo — "scores" (plural), not "score".
    # This was the actual cause of the last failure, not a memory
    # issue at all.
    results = vector_store.similarity_search_with_relevance_scores(
        rewritten_query,
        k=final_k,
        filter={
            "$and": [
                {"user_id": str(user_id)},
                {"conversation_id": str(conversation_id)},
            ]
        },
    )

    documents = []

    for document, score in results:
        document.metadata["relevance_score"] = score
        documents.append(document)

    return {
        "original_query": question,
        "rewritten_query": rewritten_query,
        "documents": documents,
    }