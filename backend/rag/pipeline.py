from rag.llm import get_llm
from rag.prompts.rag_prompt import RAG_PROMPT
from rag.prompts.normal_prompt import NORMAL_PROMPT
from rag.retrievers.rag_retriever import retrieve_documents

# >>> CHANGED: threshold scale changed. Previously this compared
# against the cross-encoder's raw relevance score (roughly
# negative-to-positive). Now that retrieval uses
# similarity_search_with_relevance_score directly (no reranker),
# scores are normalized to roughly 0-1, higher = more relevant.
# 0.5 is a reasonable starting point — test with real questions and
# adjust up (stricter) or down (more lenient) based on whether
# irrelevant answers leak into RAG mode, or relevant ones get
# wrongly treated as normal chat.
RELEVANCE_THRESHOLD = 0.5


def format_documents(documents):
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
    if not documents:
        return False

    top_score = documents[0].metadata.get("relevance_score")

    if top_score is None:
        return True

    return top_score >= RELEVANCE_THRESHOLD


def run_rag(
    question: str,
    user_id: str,
    conversation_id: str,
    has_documents: bool,
    chat_history: str = "",
    final_k: int = 5,
):
    llm = get_llm()

    if not has_documents:
        prompt = build_normal_prompt(question, chat_history)
        response = llm.invoke(prompt)

        return {
            "answer": response.content,
            "original_query": question,
            "rewritten_query": question,
            "documents": [],
        }

    retrieval_result = retrieve_documents(
        question=question,
        user_id=user_id,
        conversation_id=conversation_id,
        chat_history=chat_history,
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
    final_k: int = 5,
):
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