from rag.retrievers.query_rewriter import rewrite_query
from rag.vectorstore.chroma_store import get_vector_store


def retrieve_documents(
    question: str,
    user_id: str,
    conversation_id: str,
    chat_history: str = "",
    final_k: int = 5,
):
    """
    Retrieve relevant chunks directly via vector similarity search —
    no cross-encoder reranking step. This removes the last locally
    loaded torch-based model from the pipeline, which was the
    remaining cause of Render's free-tier memory limit being
    exceeded (embeddings already moved to a remote API earlier;
    the reranker was the last local model left).
    """

    rewritten_query = rewrite_query(
        question=question,
        chat_history=chat_history,
    )

    vector_store = get_vector_store()

    # >>> CHANGED: similarity_search_with_relevance_score returns
    # (document, score) pairs with score normalized to roughly
    # 0-1 (higher = more relevant), so pipeline.py's relevance
    # check can work the same way it did with the reranker's score
    # — just note the threshold value likely needs retuning since
    # the scale/meaning differs from the cross-encoder's score.
    results = vector_store.similarity_search_with_relevance_score(
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