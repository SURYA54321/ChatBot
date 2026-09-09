
from rag.llm import get_llm
from rag.prompts.query_rewrite import QUERY_REWRITE_PROMPT


def needs_rewriting(question: str, chat_history: str) -> bool:
    """
    Determine if query needs context from chat history.
    """
    if not chat_history.strip():
        return False
    
    # Words indicating reference to previous context
    context_words = {
        'it', 'this', 'that', 'they', 'he', 'she', 'them',
        'those', 'these', 'his', 'her', 'their', 'its',
        'also', 'too', 'more', 'another', 'same', 'above',
        'below', 'previous', 'earlier', 'later'
    }
    
    words = set(question.lower().split())
    
    has_context_ref = bool(words & context_words)
    is_very_short = len(words) < 4
    
    return has_context_ref or is_very_short


def rewrite_query(
    question: str,
    chat_history: str = "",
) -> str:
    
    # ✅ Skip LLM call for standalone questions
    if not needs_rewriting(question, chat_history):
        print("  ⏭️  Skipping rewrite (standalone question)")
        return question
    
    print("  🔄 Rewriting query with context...")
    
    llm = get_llm()
    chain = QUERY_REWRITE_PROMPT | llm

    response = chain.invoke(
        {
            "chat_history": chat_history,
            "question": question,
        }
    )

    return response.content.strip()
# Original

# from rag.llm import get_llm
# from rag.prompts.query_rewrite import QUERY_REWRITE_PROMPT


# def rewrite_query(
#     question: str,
#     chat_history: str = "",
# ) -> str:

#     llm = get_llm()

#     chain = QUERY_REWRITE_PROMPT | llm

#     response = chain.invoke(
#         {
#             "chat_history": chat_history,
#             "question": question,
#         }
#     )

#     return response.content.strip()
