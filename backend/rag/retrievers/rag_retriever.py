import time

from rag.retrievers.query_rewriter import rewrite_query
from rag.retrievers.reranking_retriever import (
    get_reranking_retriever,
)


def retrieve_documents(
    question: str,
    user_id: str,
    conversation_id: str,
    chat_history: str = "",
    initial_k: int = 7,
    final_k: int = 5,
):
    # Query rewriting
    rewritten_query = rewrite_query(
        question=question,
        chat_history=chat_history,
    )

    # Get retriever
    retriever = get_reranking_retriever(
        user_id=user_id,
        conversation_id=conversation_id,
        initial_k=initial_k,
        final_k=final_k,
    )

    # Retrieve and rerank
    documents = retriever.invoke(rewritten_query)

    return {
        "original_query": question,
        "rewritten_query": rewritten_query,
        "documents": documents,
    }