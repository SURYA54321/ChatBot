import logging
from rag.llm import get_llm
from rag.prompts.rag_prompt import RAG_PROMPT
from rag.prompts.normal_prompt import NORMAL_PROMPT
from rag.retrievers.rag_retriever import retrieve_documents
from langchain_community.document_loaders import PyPDFLoader

logger = logging.getLogger(__name__)
NORMAL_CHAT_PHRASES = {
    "hi",
    "hello",
    "hey",
    "how are you",
    "how are you?",
    "good morning",
    "good afternoon",
    "good evening",
    "thanks",
    "thank you",
    "thank you!",
    "bye",
}

def _is_document_level_question(question: str) -> bool:
    """
    Detects questions that clearly ask about the uploaded document
    as a whole rather than a specific topic.
    """
    normalized = " ".join(question.lower().strip().split())

    document_phrases = (
        "explain the document",
        "explain this document",
        "explain the pdf",
        "explain this pdf",
        "summarize the document",
        "summarize this document",
        "summarise the document",
        "summarise this document",
        "summarize the pdf",
        "summarise the pdf",
        "what is this document about",
        "what is the document about",
        "what does this document contain",
        "tell me about this document",
        "give me a summary of the document",
        "give me a summary of this document",
    )

    return normalized in document_phrases

def _is_obvious_normal_chat(question: str) -> bool:
    """
    Detects very common casual messages that do not need document retrieval.
    """
    normalized = " ".join(question.lower().strip().split())

    return normalized in NORMAL_CHAT_PHRASES

# Threshold scale for cosine similarity search (0.0 to 1.0).
# Scores >= 0.3 trigger RAG context injection; lower scores fall back to standard LLM chat.
RELEVANCE_THRESHOLD = 0.3

def process_uploaded_document(document_instance):
    file_path = document_instance.file.path
    
    # 1. Load Document
    loader = PyPDFLoader(file_path)
    raw_docs = loader.load()
    
    # 2. Check if ANY text was extracted
    extracted_text = "".join([doc.page_content for doc in raw_docs]).strip()
    
    if not extracted_text:
        logger.error(
            "Extraction Failed: File %s contains no selectable text (possibly scanned PDF).",
            document_instance.filename
        )
        document_instance.status = "FAILED"
        document_instance.error_message = "No text could be extracted. The file may be scanned or image-based."
        document_instance.save()
        raise ValueError("File contains no selectable text. Please upload a digital text document or perform OCR.")

    # 3. Chunk Text
    chunks = text_splitter.split_documents(raw_docs)
    logger.info("Successfully created %d text chunks for file %s", len(chunks), document_instance.filename)
    
    if not chunks:
        document_instance.status = "FAILED"
        document_instance.save()
        raise ValueError("Failed to create text chunks from document.")

    # 4. Store in Vector DB
    vector_store.add_documents(chunks)
    
    # 5. Mark as READY
    document_instance.status = "READY"
    document_instance.save()
    return len(chunks)

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

# New Code

def _is_relevant(documents, threshold=0.2) -> bool:
    """
    Checks if the top retrieved document is relevant.

    Our vector store uses cosine similarity:
    higher score = more relevant.
    """
    if not documents:
        return False

    top_doc = documents[0]

    top_score = top_doc.metadata.get("relevance_score")

    if top_score is None:
        top_score = top_doc.metadata.get("score")

    if top_score is None:
        logger.warning(
            "No relevance score found for retrieved document."
        )
        return False

    score_val = float(top_score)

    logger.warning(
        "RAG Relevance Check - Top similarity score: %.4f "
        "(Threshold: %.4f)",
        score_val,
        threshold,
    )

    # Cosine similarity: HIGHER score = MORE relevant.
    return score_val >= threshold

# Running code

# def _is_relevant(documents, threshold=0.4) -> bool:
#     """
#     Checks if top retrieved document passes the minimum relevance threshold.
#     Uses distance metric logic: LOWER score means HIGHER relevance.
#     """
#     if not documents:
#         return False

#     top_doc = documents[0]
#     top_score = top_doc.metadata.get("relevance_score")
    
#     if top_score is None:
#         top_score = top_doc.metadata.get("score")

#     # If your vector store doesn't attach a score metadata, pass it through safely
#     if top_score is None:
#         return True

#     score_val = float(top_score)
#     logger.info("RAG Relevance Check - Top distance score: %s (Max Threshold: %s)", score_val, threshold)

#     # DISTANCE LOGIC: Lower score means closer match. 
#     # If the distance is less than or equal to the threshold, it is relevant.
#     return score_val <= threshold
#     """
#     Checks if top retrieved document passes the minimum relevance threshold.
#     Switches between RAG mode and standard chat dynamically.
#     """
#     if not documents:
#         return False

#     top_doc = documents[0]
#     top_score = top_doc.metadata.get("relevance_score")
    
#     if top_score is None:
#         top_score = top_doc.metadata.get("score")

#     # If your vector store doesn't attach a score, allow it through
#     if top_score is None:
#         return True

#     # LOG the score so you can monitor threshold behavior in Render logs
#     logger.info("RAG Relevance Check - Top score: %s (Threshold: %s)", top_score, threshold)

#     # NOTE ON SCORES:
#     # 1. If your vector DB returns SIMILARITY (higher is better, e.g., 0 to 1): use >=
#     # 2. If your vector DB returns DISTANCE (lower is better, e.g., 0.1 is close): use <=
    
#     return float(top_score) >= threshold

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

    if _is_obvious_normal_chat(question):
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
    if not _is_relevant(documents) and not _is_document_level_question(question):
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

    if _is_obvious_normal_chat(question):
        prompt = build_normal_prompt(question, chat_history)

        for chunk in llm.stream(prompt):
            if chunk.content:
                yield {
                    "type": "token",
                    "content": chunk.content,
                }

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

    if not _is_relevant(documents) and not _is_document_level_question(question):
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