from functools import lru_cache

from langchain_huggingface import HuggingFaceEndpointEmbeddings


@lru_cache(maxsize=1)
def get_embedding_model():
     return HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
    )


# from langchain_huggingface import HuggingFaceEmbeddings


# def get_embedding_model():
#     return HuggingFaceEmbeddings(
#         model_name="intfloat/multilingual-e5-small",
#         encode_kwargs={
#             "normalize_embeddings": True,
#         },
#     )
