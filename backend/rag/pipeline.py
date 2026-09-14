import logging
from rag.llm import get_llm
from rag.prompts.rag_prompt import RAG_PROMPT
from rag.prompts.normal_prompt import NORMAL_PROMPT
from rag.retrievers.rag_retriever import retrieve_documents

logger = logging.getLogger(__name__)

# Threshold scale for cosine similarity search (0.0 to 1.0).
# Scores >= 0.3 trigger RAG context injection; lower scores fall back to standard LLM chat.
RELEVANCE_THRESHOLD = 0.3


def format_documents(documents) -> str:
    """Formats retrieved document chunks into context string for RAG prompt."""
    if not documents:
        return "No relevant documents were found."

    formatted_documents = []

    for index, document in enumerate(documents, start=1):
        metadata = document.metadata

        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        page = metadata.get("page")

        source = filename
        if page is not None:
            source = f"{filename}, page {page + 1}"

        formatted_documents.append(
            f"[Document {index}]\nSource: {source}\n\n{document.page_content}"
        )

    return "\n\n".join(formatted_documents)


def build_rag_prompt(question: str, chat_history: str, documents):
    """Builds RAG prompt template with retrieved context."""
    context = format_documents(documents)

    return RAG_PROMPT.invoke(
        {
            "question": question,
            "chat_history": chat_history,
            "context": context,
        }
    )


def build_normal_prompt(question: str, chat_history: str):
    """Builds standard prompt template for normal chat."""
    return NORMAL_PROMPT.invoke(
        {
            "question": question,
            "chat_history": chat_history,
        }
    )


def _is_relevant(documents, threshold=0.3) -> bool:
    """
    Checks if top retrieved document passes the minimum relevance threshold.
    Switches between RAG mode and standard chat dynamically.
    """
    if not documents:
        return False

    top_doc = documents[0]
    top_score = top_doc.metadata.get("relevance_score")
    
    if top_score is None:
        top_score = top_doc.metadata.get("score")

    # If your vector store doesn't attach a score, allow it through
    if top_score is None:
        return True

    # LOG the score so you can monitor threshold behavior in Render logs
    logger.info("RAG Relevance Check - Top score: %s (Threshold: %s)", top_score, threshold)

    # NOTE ON SCORES:
    # 1. If your vector DB returns SIMILARITY (higher is better, e.g., 0 to 1): use >=
    # 2. If your vector DB returns DISTANCE (lower is better, e.g., 0.1 is close): use <=
    
    return float(top_score) >= threshold

def run_rag(
    question: str,
    user_id: str,
    conversation_id: str,
    has_documents: bool,
    chat_history: str = "",
    final_k: int = 5,
):
    """
    Executes non-streaming RAG or standard chat depending on document presence and relevance.
    """
    llm = get_llm()

    # Case 1: No documents uploaded in this conversation
    if not has_documents:
        prompt = build_normal_prompt(question, chat_history)
        response = llm.invoke(prompt)

        return {
            "answer": response.content,
            "original_query": question,
            "rewritten_query": question,
            "documents": [],
        }

    # Case 2: Retrieve documents from SQLite
    retrieval_result = retrieve_documents(
        question=question,
        user_id=user_id,
        conversation_id=conversation_id,
        chat_history=chat_history,
        final_k=final_k,
    )

    documents = retrieval_result.get("documents", [])
    rewritten_query = retrieval_result.get("rewritten_query", question)

    # Case 3: Documents retrieved fall below relevance threshold
    if not _is_relevant(documents):
        prompt = build_normal_prompt(question, chat_history)
        response = llm.invoke(prompt)

        return {
            "answer": response.content,
            "original_query": question,
            "rewritten_query": rewritten_query,
            "documents": [],
        }

    # Case 4: Relevant documents found -> Run RAG
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
    """
    Executes streaming RAG (Server-Sent Events tokens) or standard streaming chat.
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
        final_k=final_k,
    )

    documents = retrieval_result.get("documents", [])
    rewritten_query = retrieval_result.get("rewritten_query", question)

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