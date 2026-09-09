from rag.pipeline import build_rag_prompt


question = "What is Django middleware?"


chat_history = """
User: I am learning Django.
Assistant: Django is a Python web framework.
"""


documents = [
    type(
        "Document",
        (),
        {
            "page_content": (
                "Django middleware is a framework component "
                "that processes requests and responses."
            ),
            "metadata": {
                "filename": "django.txt",
                "file_type": "txt",
            },
        },
    )()
]


prompt = build_rag_prompt(
    question=question,
    chat_history=chat_history,
    documents=documents,
)


for message in prompt.messages:
    print("\n" + "=" * 60)
    print(message.type.upper())
    print("=" * 60)
    print(message.content)
