from rag.llm import get_llm
from rag.prompts.rag_prompt import RAG_PROMPT
from rag.prompts.normal_prompt import NORMAL_PROMPT
from rag.retrievers.rag_retriever import retrieve_documents

# >>> NEW: cross-encoder relevance score cutoff. CrossEncoderReranker
# attaches a "relevance_score" to each document's metadata after
# reranking. ms-marco style cross-encoders produce roughly
# positive-for-relevant / negative-for-irrelevant scores, so 0.0 is a
# reasonable default cutoff. Raise it if you see irrelevant context
# still leaking through; lower it if relevant answers get skipped.
RELEVANCE_THRESHOLD = 0.0


def format_documents(documents):
    """
    Convert retrieved LangChain documents into a context string.
    """

    if not documents:
        return "No relevant documents were found."

    formatted_documents = []

    for index, document in enumerate(documents, start=1):
        metadata = document.metadata

        filename = metadata.get("filename", "Unknown")
        page = metadata.get("page")

        source = filename

        if page is not None:
            source = f"{filename}, page {page + 1}"

        formatted_documents.append(
            f"""[Document {index}]
Source: {source}

{document.page_content}
"""
        )

    return "\n\n".join(formatted_documents)


def build_rag_prompt(question: str, chat_history: str, documents):
    context = format_documents(documents)

    return RAG_PROMPT.invoke(
        {
            "question": question,
            "chat_history": chat_history,
            "context": context,
        }
    )


def build_normal_prompt(question: str, chat_history: str):
    return NORMAL_PROMPT.invoke(
        {
            "question": question,
            "chat_history": chat_history,
        }
    )


def _is_relevant(documents) -> bool:
    """
    >>> NEW: decides RAG vs normal chat using the reranker's own
    score — no extra LLM call needed, so this adds ~0ms to latency.
    """
    if not documents:
        return False

    top_score = documents[0].metadata.get("relevance_score")

    if top_score is None:
        # Reranker didn't attach a score for some reason — fail safe
        # by treating retrieval as relevant rather than silently
        # dropping context.
        return True

    return top_score >= RELEVANCE_THRESHOLD


def run_rag(
    question: str,
    user_id: str,
    conversation_id: str,
    has_documents: bool,
    chat_history: str = "",
    initial_k: int = 7,
    final_k: int = 5,
):
    """
    Complete pipeline. Routes between normal chat and RAG depending
    on whether the current conversation has documents AND whether
    retrieval actually found something relevant.
    """

    llm = get_llm()

    # --------------------------------------------------
    # No documents in this chat at all -> skip retrieval entirely.
    # --------------------------------------------------
    if not has_documents:
        prompt = build_normal_prompt(question, chat_history)
        response = llm.invoke(prompt)

        return {
            "answer": response.content,
            "original_query": question,
            "rewritten_query": question,
            "documents": [],
        }

    # --------------------------------------------------
    # Documents exist -> retrieve + rerank, then decide relevance.
    # --------------------------------------------------
    retrieval_result = retrieve_documents(
        question=question,
        user_id=user_id,
        conversation_id=conversation_id,
        chat_history=chat_history,
        initial_k=initial_k,
        final_k=final_k,
    )

    documents = retrieval_result["documents"]
    rewritten_query = retrieval_result["rewritten_query"]

    if not _is_relevant(documents):
        prompt = build_normal_prompt(question, chat_history)
        response = llm.invoke(prompt)

        return {
            "answer": response.content,
            "original_query": question,
            "rewritten_query": rewritten_query,
            "documents": [],
        }

    prompt = build_rag_prompt(question, chat_history, documents)
    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "original_query": question,
        "rewritten_query": rewritten_query,
        "documents": documents,
    }


def stream_rag(
    question: str,
    user_id: str,
    conversation_id: str,
    has_documents: bool,
    chat_history: str = "",
    initial_k: int = 7,
    final_k: int = 5,
):
    """
    Stream the final LLM response while keeping retrieval and
    reranking non-streaming. Same routing logic as run_rag.
    """

    llm = get_llm()

    if not has_documents:
        prompt = build_normal_prompt(question, chat_history)

        for chunk in llm.stream(prompt):
            if chunk.content:
                yield {"type": "token", "content": chunk.content}

        yield {
            "type": "done",
            "rewritten_query": question,
            "documents": [],
        }
        return

    retrieval_result = retrieve_documents(
        question=question,
        user_id=user_id,
        conversation_id=conversation_id,
        chat_history=chat_history,
        initial_k=initial_k,
        final_k=final_k,
    )

    documents = retrieval_result["documents"]
    rewritten_query = retrieval_result["rewritten_query"]

    if not _is_relevant(documents):
        prompt = build_normal_prompt(question, chat_history)

        for chunk in llm.stream(prompt):
            if chunk.content:
                yield {"type": "token", "content": chunk.content}

        yield {
            "type": "done",
            "rewritten_query": rewritten_query,
            "documents": [],
        }
        return

    prompt = build_rag_prompt(question, chat_history, documents)

    for chunk in llm.stream(prompt):
        if chunk.content:
            yield {"type": "token", "content": chunk.content}

    yield {
        "type": "done",
        "rewritten_query": rewritten_query,
        "documents": documents,
    }