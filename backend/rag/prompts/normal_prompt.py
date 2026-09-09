from langchain_core.prompts import ChatPromptTemplate


NORMAL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful, friendly AI assistant.

Answer the user's question directly using your own knowledge and the
conversation history below.

Rules:

1. You may use conversation history to understand references and
   follow-up questions.
2. Keep the answer clear and useful.
3. Do not mention retrieval, embeddings, vector databases, rerankers,
   or documents unless the user brings them up first.

Conversation history:

{chat_history}
""",
        ),
        (
            "human",
            "{question}",
        ),
    ]
)