from rag.retrievers.query_rewriter import rewrite_query
from rag.retrievers.reranking_retriever import (
    get_reranking_retriever,
)
from rag.reranker.cross_encoder import get_reranker_model
import time 


# Further Duplicate


def retrieve_documents(
    question: str,
    user_id: str,
    chat_history: str = "",
    initial_k: int = 20,
    final_k: int = 5,
):
    print(f"\n  📝 Retrieving documents...")

    # Query rewriting
    t1 = time.time()
    rewritten_query = rewrite_query(
        question=question,
        chat_history=chat_history,
    )
    rewrite_time = time.time() - t1
    print(f"  ⏱️   Query rewriting: {rewrite_time:.2f}s")

    # Get retriever + compressor
    t2 = time.time()
    base_retriever, compressor = get_reranking_retriever(
        user_id=user_id,
        initial_k=initial_k,
        final_k=final_k,
    )
    setup_time = time.time() - t2
    print(f"  ⏱️   Retriever setup: {setup_time:.2f}s")

    # Vector search (Chroma)
    t3 = time.time()
    candidates = base_retriever.invoke(rewritten_query)
    vector_time = time.time() - t3
    print(f"  ⏱️   Vector search: {vector_time:.2f}s ({len(candidates)} candidates)")

    # Reranking via LangChain wrapper
    t4 = time.time()
    documents = compressor.compress_documents(candidates, rewritten_query)
    rerank_time = time.time() - t4
    print(f"  ⏱️   Reranking: {rerank_time:.2f}s")

    # --- TEMPORARY DIAGNOSTIC: raw model call, bypassing LangChain ---
    reranker_model = get_reranker_model()
    pairs = [(rewritten_query, doc.page_content) for doc in candidates]
    print(f"  📏 Pair count: {len(pairs)}, avg length: {sum(len(p[1]) for p in pairs)//len(pairs)} chars")

    t5 = time.time()
    raw_scores = reranker_model.score(pairs)
    print(f"  ⏱️   Raw .score() call: {time.time() - t5:.2f}s")
    # --- END DIAGNOSTIC ---

    return {
        "original_query": question,
        "rewritten_query": rewritten_query,
        "documents": documents,
    }
# Duplicate
# def retrieve_documents(
#     question: str,
#     user_id: str,
#     chat_history: str = "",
#     initial_k: int = 5,
#     final_k: int = 5,
# ):
#     print(f"\n  📝 Retrieving documents...")
    
#     # Query rewriting
#     t1 = time.time()
#     rewritten_query = rewrite_query(
#         question=question,
#         chat_history=chat_history,
#     )
#     rewrite_time = time.time() - t1
#     print(f"  ⏱️   Query rewriting: {rewrite_time:.2f}s")
    
#     # Get retriever
#     t2 = time.time()
#     retriever = get_reranking_retriever(
#         user_id=user_id,
#         initial_k=initial_k,
#         final_k=final_k,
#     )
#     setup_time = time.time() - t2
#     print(f"  ⏱️   Retriever setup: {setup_time:.2f}s")
    
#     # Retrieve and rerank
#     t3 = time.time()
#     documents = retriever.invoke(
#         rewritten_query
#     )
#     search_time = time.time() - t3
#     print(f"  ⏱️   Vector search + reranking: {search_time:.2f}s")
    
#     return {
#         "original_query": question,
#         "rewritten_query": rewritten_query,
#         "documents": documents,
#     }

# Original
# def retrieve_documents(
#     question: str,
#     user_id: str,
#     chat_history: str = "",
#     initial_k: int = 20,
#     final_k: int = 5,
# ):
#     rewritten_query = rewrite_query(
#         question=question,
#         chat_history=chat_history,
#     )

#     retriever = get_reranking_retriever(
#         user_id=user_id,
#         initial_k=initial_k,
#         final_k=final_k,
#     )

#     documents = retriever.invoke(
#         rewritten_query
#     )

#     return {
#         "original_query": question,
#         "rewritten_query": rewritten_query,
#         "documents": documents,
#     }
