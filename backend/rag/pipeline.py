from rag.llm import get_llm
from rag.prompts.rag_prompt import RAG_PROMPT
from rag.retrievers.rag_retriever import retrieve_documents
import time 

def format_documents(documents):
    """
    Convert retrieved LangChain documents into a context string.
    """

    if not documents:
        return "No relevant documents were found."

    formatted_documents = []

    for index, document in enumerate(
        documents,
        start=1,
    ):
        metadata = document.metadata

        filename = metadata.get(
            "filename",
            "Unknown",
        )

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


def build_rag_prompt(
    question: str,
    chat_history: str,
    documents,
):
    context = format_documents(documents)

    return RAG_PROMPT.invoke(
        {
            "question": question,
            "chat_history": chat_history,
            "context": context,
        }
    )


# Duplicate 

def run_rag(
    question: str,
    user_id: str,
    chat_history: str = "",
    initial_k: int = 10,
    final_k: int = 5,
):
    """
    Complete RAG pipeline.
    """
    
    start_time = time.time()
    
    # Retrieval
    t1 = time.time()
    retrieval_result = retrieve_documents(
        question=question,
        user_id=user_id,
        chat_history=chat_history,
        initial_k=initial_k,
        final_k=final_k,
    )
    print(f"⏱️ Retrieval: {time.time() - t1:.2f}s")
    
    documents = retrieval_result["documents"]
    rewritten_query = retrieval_result["rewritten_query"]
    
    # Build prompt
    t2 = time.time()
    prompt = build_rag_prompt(
        question=question,
        chat_history=chat_history,
        documents=documents,
    )
    print(f"⏱️ Prompt building: {time.time() - t2:.2f}s")
    
    # LLM generation
    t3 = time.time()
    llm = get_llm()
    response = llm.invoke(prompt)
    print(f"⏱️ LLM generation: {time.time() - t3:.2f}s")
    
    print(f"⏱️ TOTAL: {time.time() - start_time:.2f}s")
    
    return {
        "answer": response.content,
        "original_query": question,
        "rewritten_query": rewritten_query,
        "documents": documents,
    }

#  Original
# def run_rag(
#     question: str,
#     user_id: str,
#     chat_history: str = "",
#     initial_k: int = 20,
#     final_k: int = 5,
# ):
#     """
#     Complete RAG pipeline.

#     Returns:
#         answer
#         retrieved documents
#         rewritten query
#     """

#     retrieval_result = retrieve_documents(
#         question=question,
#         user_id=user_id,
#         chat_history=chat_history,
#         initial_k=initial_k,
#         final_k=final_k,
#     )

#     documents = retrieval_result["documents"]

#     rewritten_query = retrieval_result[
#         "rewritten_query"
#     ]

#     prompt = build_rag_prompt(
#         question=question,
#         chat_history=chat_history,
#         documents=documents,
#     )

#     llm = get_llm()

#     response = llm.invoke(prompt)

#     return {
#         "answer": response.content,
#         "original_query": question,
#         "rewritten_query": rewritten_query,
#         "documents": documents,
#     }




# Duplicate
def stream_rag(
    question: str,
    user_id: str,
    chat_history: str = "",
    initial_k: int = 20,
    final_k: int = 5,
):
    """
    Stream the final LLM response while keeping
    retrieval and reranking non-streaming.
    """
    
    start_time = time.time()
    print(f"\n{'='*60}")
    print(f"🚀 RAG STREAMING PIPELINE STARTED")
    print(f"{'='*60}")
    
    # Retrieval (non-streaming)
    t1 = time.time()
    retrieval_result = retrieve_documents(
        question=question,
        user_id=user_id,
        chat_history=chat_history,
        initial_k=initial_k,
        final_k=final_k,
    )
    retrieval_time = time.time() - t1
    print(f"⏱️  Retrieval: {retrieval_time:.2f}s")
    
    documents = retrieval_result["documents"]
    
    # Build prompt
    t2 = time.time()
    prompt = build_rag_prompt(
        question=question,
        chat_history=chat_history,
        documents=documents,
    )
    prompt_time = time.time() - t2
    print(f"⏱️  Prompt building: {prompt_time:.2f}s")
    
    # LLM streaming
    print(f"⏱️  LLM streaming started...")
    llm = get_llm()
    
    llm_start = time.time()
    for chunk in llm.stream(prompt):
        if chunk.content:
            yield {
                "type": "token",
                "content": chunk.content,
            }
    llm_time = time.time() - llm_start
    print(f"⏱️  LLM streaming: {llm_time:.2f}s")
    
    total_time = time.time() - start_time
    print(f"{'='*60}")
    print(f"⏱️  TOTAL: {total_time:.2f}s")
    print(f"{'='*60}\n")
    
    yield {
        "type": "done",
        "rewritten_query": retrieval_result["rewritten_query"],
        "documents": documents,
    }


# Original
# def stream_rag(
#     question: str,
#     user_id: str,
#     chat_history: str = "",
#     initial_k: int = 20,
#     final_k: int = 5,
# ):
#     """
#     Stream the final LLM response while keeping
#     retrieval and reranking non-streaming.
#     """

#     retrieval_result = retrieve_documents(
#         question=question,
#         user_id=user_id,
#         chat_history=chat_history,
#         initial_k=initial_k,
#         final_k=final_k,
#     )

#     documents = retrieval_result["documents"]

#     prompt = build_rag_prompt(
#         question=question,
#         chat_history=chat_history,
#         documents=documents,
#     )

#     llm = get_llm()

#     for chunk in llm.stream(prompt):
#         if chunk.content:
#             yield {
#                 "type": "token",
#                 "content": chunk.content,
#             }

#     yield {
#         "type": "done",
#         "rewritten_query": retrieval_result[
#             "rewritten_query"
#         ],
#         "documents": documents,
#     }
