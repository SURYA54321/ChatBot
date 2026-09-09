from rag.pipeline import run_rag


question = "What is Django used for?"

chat_history = ""


result = run_rag(
    question=question,
    user_id="test-user-1",
    chat_history=chat_history,
)


print("\n" + "=" * 60)
print("ANSWER")
print("=" * 60)

print(result["answer"])


print("\n" + "=" * 60)
print("REWRITTEN QUERY")
print("=" * 60)

print(result["rewritten_query"])


print("\n" + "=" * 60)
print("SOURCES")
print("=" * 60)


for index, document in enumerate(
    result["documents"],
    start=1,
):
    print(
        f"\n{index}. "
        f"{document.metadata.get('filename')}"
    )
