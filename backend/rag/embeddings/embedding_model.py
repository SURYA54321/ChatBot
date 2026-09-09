from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings


@lru_cache(maxsize=1)
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-small",
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )


# from langchain_huggingface import HuggingFaceEmbeddings


# def get_embedding_model():
#     return HuggingFaceEmbeddings(
#         model_name="intfloat/multilingual-e5-small",
#         encode_kwargs={
#             "normalize_embeddings": True,
#         },
#     )
