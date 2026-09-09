from rag.vectorstore.chroma_store import similarity_search


query = "What is Django used for?"

results = similarity_search(
    query=query,
    user_id="test-user-1",
    k=20,
)


print(f"Results found: {len(results)}")


for index, document in enumerate(results):
    print("\n" + "=" * 60)
    print(f"RESULT {index + 1}")
    print("=" * 60)

    print(document.page_content)

    print("\nMETADATA:")
    print(document.metadata)
