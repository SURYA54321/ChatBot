from functools import lru_cache

from langchain_classic.retrievers.contextual_compression import (
    ContextualCompressionRetriever,
)
from langchain_classic.retrievers.document_compressors import (
    CrossEncoderReranker,
)

from rag.reranker.cross_encoder import get_reranker_model
from Pre_project.backend.rag.vectorstore.simple_store import get_vector_store


@lru_cache(maxsize=1)
def _get_cached_compressor(final_k: int):
    """
    Create and cache the reranker compressor.
    This is shared across all users.
    """
    reranker_model = get_reranker_model()

    compressor = CrossEncoderReranker(
        model=reranker_model,
        top_n=final_k,
    )
    return compressor


def get_reranking_retriever(
    user_id: str,
    conversation_id: str,
    initial_k: int = 7,
    final_k: int = 5,
):
    """
    Create a retriever scoped to one user's one conversation.
    Uses the cached compressor to avoid reloading the model.
    """
    vector_store = get_vector_store()

    # >>> CHANGED: filter by BOTH user_id and conversation_id.
    # This is the actual fix for cross-chat/cross-user document
    # leakage — this is the retriever the live chat pipeline uses.
    base_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": initial_k,
            "filter": {
                "$and": [
                    {"user_id": str(user_id)},
                    {"conversation_id": str(conversation_id)},
                ]
            },
        },
    )

    compressor = _get_cached_compressor(final_k)

    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever,
    )


def retrieve_and_rerank(
    query: str,
    user_id: str,
    conversation_id: str,
    initial_k: int = 7,
    final_k: int = 5,
):
    retriever = get_reranking_retriever(
        user_id=user_id,
        conversation_id=conversation_id,
        initial_k=initial_k,
        final_k=final_k,
    )

    return retriever.invoke(query)