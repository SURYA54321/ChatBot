from dotenv import load_dotenv

load_dotenv()

from rag.llm import get_llm



llm = get_llm()

response = llm.invoke(
    "Explain what RAG is in two sentences."
)

print(response.content)