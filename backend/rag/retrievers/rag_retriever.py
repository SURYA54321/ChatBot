import logging
from typing import List, Dict, Any
from langchain_core.documents import Document
from rag.embeddings.embedding_model import get_embedding_model
from rag.vectorstore.simple_store import similarity_search_with_relevance_scores

logger = logging.getLogger(__name__)


def retrieve_documents(
    question: str = None,
    query: str = None,
    user_id: Any = None,
    conversation_id: Any = None,
    chat_history: str = "",
    final_k: int = 5,
    top_k: int = 5,
    score_threshold: float = 0.2,
) -> Dict[str, Any]:
    """
    Retrieves relevant document chunks from SQLite using vector cosine similarity.
    Compatible with both positional and keyword arguments from run_rag / stream_rag.
    """
    search_query = question or query or ""
    k = final_k or top_k or 5

    try:
        embedding_model = get_embedding_model()

        # Perform lightweight vector search in SQLite via NumPy
        scored_results = similarity_search_with_relevance_scores(
            query=search_query,
            user_id=user_id,
            conversation_id=conversation_id,
            embedding_model=embedding_model,
            k=k,
            score_threshold=score_threshold,
        )

        # Convert matched chunks to standard LangChain Document objects
        retrieved_docs: List[Document] = []
        for chunk, score in scored_results:
            doc = Document(
                page_content=chunk.content,
                metadata={
                    "chunk_id": str(chunk.id),
                    "chunk_index": chunk.chunk_index,
                    "filename": getattr(chunk, "filename", "uploaded_doc"),
                    "source": getattr(chunk, "filename", "uploaded_doc"),
                    "page": getattr(chunk, "page", None),
                    "score": float(score),
                    "relevance_score": float(score),  # Read by _is_relevant()
                },
            )
            retrieved_docs.append(doc)

        logger.info(
            f"Retrieved {len(retrieved_docs)} chunks for conversation {conversation_id}."
        )

        return {
            "documents": retrieved_docs,
            "rewritten_query": search_query,
        }

    except Exception as e:
        logger.error(f"Error during document retrieval: {str(e)}")
        return {
            "documents": [],
            "rewritten_query": search_query,
        }