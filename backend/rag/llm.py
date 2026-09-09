import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from functools import lru_cache


load_dotenv()

@lru_cache(maxsize=1)
def get_llm():
    return ChatGroq(
        model=os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b",
        ),
        temperature=0.2,
        max_tokens=2048,
        api_key=os.getenv("GROQ_API_KEY"),
    )
