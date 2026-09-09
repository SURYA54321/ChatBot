# Further Duplicate
from functools import lru_cache

from langchain_classic.retrievers.contextual_compression import (
    ContextualCompressionRetriever,
)
from langchain_classic.retrievers.document_compressors import (
    CrossEncoderReranker,
)

from rag.reranker.cross_encoder import get_reranker_model
from rag.vectorstore.chroma_store import get_vector_store
from rag.utils.timing import timed


@lru_cache(maxsize=1)
def _get_cached_compressor(final_k: int):
    print("🔧 Creating cached reranker compressor...")
    reranker_model = get_reranker_model()

    compressor = CrossEncoderReranker(
        model=reranker_model,
        top_n=final_k,
    )
    print("✅ Compressor cached and ready!")
    return compressor


def get_reranking_retriever(
    user_id: str,
    initial_k: int = 7,
    final_k: int = 5,
):
    vector_store = get_vector_store()

    base_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": initial_k,
            "filter": {
                "user_id": str(user_id),
            },
        },
    )

    compressor = _get_cached_compressor(final_k)

    return base_retriever, compressor


def retrieve_and_rerank(
    query: str,
    user_id: str,
    initial_k: int = 7,
    final_k: int = 5,
):
    base_retriever, compressor = get_reranking_retriever(
        user_id=user_id,
        initial_k=initial_k,
        final_k=final_k,
    )

    with timed("vector_search"):
        candidates = base_retriever.invoke(query)

    with timed("reranking"):
        documents = compressor.compress_documents(candidates, query)

    return documents

# Duplicate
# from functools import lru_cache

# from langchain_classic.retrievers.contextual_compression import (
#     ContextualCompressionRetriever,
# )
# from langchain_classic.retrievers.document_compressors import (
#     CrossEncoderReranker,
# )

# from rag.reranker.cross_encoder import get_reranker_model
# from rag.vectorstore.chroma_store import get_vector_store


# # ✅ Cache the COMPRESSOR (not the retriever)
# @lru_cache(maxsize=1)
# def _get_cached_compressor(final_k: int):
#     """
#     Create and cache the reranker compressor.
#     This is shared across all users.
#     """
#     print("🔧 Creating cached reranker compressor...")
#     reranker_model = get_reranker_model()
    
#     compressor = CrossEncoderReranker(
#         model=reranker_model,
#         top_n=final_k,
#     )
#     print("✅ Compressor cached and ready!")
#     return compressor


# def get_reranking_retriever(
#     user_id: str,
#     initial_k: int = 7,
#     final_k: int = 5,
# ):
#     """
#     Create a retriever for a specific user.
#     Uses the cached compressor to avoid reloading the model.
#     """
#     vector_store = get_vector_store()

#     # User-specific retriever
#     base_retriever = vector_store.as_retriever(
#         search_type="similarity",
#         search_kwargs={
#             "k": initial_k,
#             "filter": {
#                 "user_id": str(user_id),
#             },
#         },
#     )

#     # ✅ Use the SHARED cached compressor
#     compressor = _get_cached_compressor(final_k)

#     return ContextualCompressionRetriever(
#         base_compressor=compressor,
#         base_retriever=base_retriever,
#     )


# def retrieve_and_rerank(
#     query: str,
#     user_id: str,
#     initial_k: int = 7,
#     final_k: int = 5,
# ):
#     retriever = get_reranking_retriever(
#         user_id=user_id,
#         initial_k=initial_k,
#         final_k=final_k,
#     )

#     return retriever.invoke(query)

#  Original
# from langchain_classic.retrievers.contextual_compression import (
#     ContextualCompressionRetriever,
# )
# from langchain_classic.retrievers.document_compressors import (
#     CrossEncoderReranker,
# )

# from functools import lru_cache

# from rag.reranker.cross_encoder import get_reranker_model
# from rag.vectorstore.chroma_store import get_vector_store

# @lru_cache(maxsize=1)
# def get_reranking_retriever(
#     user_id: str,
#     initial_k: int = 5,
#     final_k: int = 5,
# ):
#     vector_store = get_vector_store()

#     base_retriever = vector_store.as_retriever(
#         search_type="similarity",
#         search_kwargs={
#             "k": initial_k,
#             "filter": {
#                 "user_id": str(user_id),
#             },
#         },
#     )

#     reranker_model = get_reranker_model()

#     compressor = CrossEncoderReranker(
#         model=reranker_model,
#         top_n=final_k,
#     )

#     return ContextualCompressionRetriever(
#         base_compressor=compressor,
#         base_retriever=base_retriever,
#     )


# def retrieve_and_rerank(
#     query: str,
#     user_id: str,
#     initial_k: int = 5,
#     final_k: int = 5,
# ):
#     retriever = get_reranking_retriever(
#         user_id=user_id,
#         initial_k=initial_k,
#         final_k=final_k,
#     )

#     return retriever.invoke(query)


# from rag.reranker.cross_encoder import get_reranker_model
# from rag.vectorstore.chroma_store import similarity_search


# def rerank_documents(
#     query: str,
#     documents,
#     final_k: int = 5,
# ):
#     if not documents:
#         return []

#     reranker = get_reranker_model()

#     pairs = [
#         (query, document.page_content)
#         for document in documents
#     ]

#     scores = reranker.score(pairs)

#     ranked_documents = sorted(
#         zip(documents, scores),
#         key=lambda item: item[1],
#         reverse=True,
#     )

#     return [
#         document
#         for document, score in ranked_documents[:final_k]
#     ]


# def retrieve_and_rerank(
#     query: str,
#     user_id: str,
#     initial_k: int = 20,
#     final_k: int = 5,
# ):
#     documents = similarity_search(
#         query=query,
#         user_id=user_id,
#         k=initial_k,
#     )

#     return rerank_documents(
#         query=query,
#         documents=documents,
#         final_k=final_k,
#     )
