from rag.retrievers.query_rewriter import rewrite_query


chat_history = """
User: What is Django middleware?
Assistant: Django middleware is a framework that processes
requests and responses globally in a Django application.
"""


question = "Why is it useful?"


rewritten = rewrite_query(
    question=question,
    chat_history=chat_history,
)


print("Original question:")
print(question)

print("\nRewritten query:")
print(rewritten)
