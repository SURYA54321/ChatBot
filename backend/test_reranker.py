from rag.retrievers.reranking_retriever import (
    retrieve_and_rerank,
)


query = "What is Django used for?"


results = retrieve_and_rerank(
    query=query,
    user_id="test-user-1",
    initial_k=20,
    final_k=5,
)


print(f"Final results: {len(results)}")


for index, document in enumerate(results):
    print("\n" + "=" * 60)
    print(f"RERANKED RESULT {index + 1}")
    print("=" * 60)

    print(document.page_content)

    print("\nMETADATA:")
    print(document.metadata)
