from rag.retrievers.query_rewriter import rewrite_query
from rag.vectorstore.simple_store import similarity_search_with_relevance_scores


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

    # >>> CHANGED: no more Chroma. Plain cosine similarity over this
    # conversation's stored chunks.
    results = similarity_search_with_relevance_scores(
        rewritten_query,
        user_id=user_id,
        conversation_id=conversation_id,
        k=final_k,
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