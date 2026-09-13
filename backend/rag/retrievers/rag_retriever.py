from rag.retrievers.query_rewriter import rewrite_query
from rag.vectorstore.simple_store import (
    similarity_search_with_relevance_scores,
    get_document_order_chunks,
)

# >>> NEW: keyword-based detection for whole-document requests.
# These aren't topical questions — similarity search against
# "summarize the document" won't meaningfully match specific
# chunks, since the query and content aren't semantically similar
# text even though the request is clearly document-related.
SUMMARY_KEYWORDS = {
    "summarize", "summarise", "summary", "overview",
    "key points", "main points", "tldr", "tl;dr",
}


def is_summary_request(question: str) -> bool:
    lowered = question.lower()
    return any(keyword in lowered for keyword in SUMMARY_KEYWORDS)


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

    if is_summary_request(question):
        # >>> NEW: for whole-document requests, pull chunks in
        # document order instead of similarity-ranking against a
        # query that doesn't semantically match specific content.
        # Always treated as relevant — force_relevant lets pipeline
        # skip the score threshold for this case.
        documents = get_document_order_chunks(
            user_id=user_id,
            conversation_id=conversation_id,
            limit=final_k,
        )

        for document in documents:
            document.metadata["relevance_score"] = 1.0

        return {
            "original_query": question,
            "rewritten_query": rewritten_query,
            "documents": documents,
        }

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