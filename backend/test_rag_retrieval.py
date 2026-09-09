from rag.retrievers.rag_retriever import retrieve_documents


chat_history = """
User: What is Django middleware?
Assistant: Django middleware is a framework that processes
requests and responses globally in a Django application.
"""


question = "Why is it useful?"


result = retrieve_documents(
    question=question,
    user_id="test-user-1",
    chat_history=chat_history,
)


print("Original query:")
print(result["original_query"])

print("\nRewritten query:")
print(result["rewritten_query"])

print(
    f"\nRetrieved documents: "
    f"{len(result['documents'])}"
)


for index, document in enumerate(
    result["documents"],
    start=1,
):
    print("\n" + "=" * 60)
    print(f"RESULT {index}")
    print("=" * 60)

    print(document.page_content)

    print("\nMetadata:")
    print(document.metadata)