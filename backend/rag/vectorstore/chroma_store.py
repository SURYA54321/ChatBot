from pathlib import Path
from functools import lru_cache

from uuid import uuid4

from langchain_chroma import Chroma

from rag.embeddings.embedding_model import (
    get_embedding_model,
)


BASE_DIR = Path(__file__).resolve().parents[2]

CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "rag_documents"

@lru_cache(maxsize=1)  # ✅ ADD THIS
def get_vector_store():
    embedding_model = get_embedding_model()
    
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=str(CHROMA_DIR),
    )


# Original

# def get_vector_store():
#     embedding_model = get_embedding_model()

#     return Chroma(
#         collection_name=COLLECTION_NAME,
#         embedding_function=embedding_model,
#         persist_directory=str(CHROMA_DIR),
#     )


def add_documents(chunks):
    vector_store = get_vector_store()

    ids = [
        str(uuid4())
        for _ in chunks
    ]

    vector_store.add_documents(
        documents=chunks,
        ids=ids,
    )

    return ids


def similarity_search(
    query: str,
    user_id: str,
    k: int = 20,
):
    vector_store = get_vector_store()

    return vector_store.similarity_search(
        query,
        k=k,
        filter={
            "user_id": str(user_id)
        },
    )


def delete_document_vectors(
    document_id: str,
    user_id: str,
):
    vector_store = get_vector_store()

    collection = vector_store._collection

    collection.delete(
        where={
            "$and": [
                {
                    "document_id": str(document_id)
                },
                {
                    "user_id": str(user_id)
                },
            ]
        }
    )