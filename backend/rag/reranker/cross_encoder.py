from functools import lru_cache
from langchain_community.cross_encoders import HuggingFaceCrossEncoder


def get_reranker_model():
    print("🔄 Loading reranker model...")  # ✅ ADD THIS
    model = HuggingFaceCrossEncoder(
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
    )
    print("✅ Reranker model loaded!")  # ✅ ADD THIS
    return model

# @lru_cache(maxsize=1)  # ✅ ADD THIS
# def get_reranker_model():
#     return HuggingFaceCrossEncoder(
#         model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
#     )


# Original 

# from langchain_community.cross_encoders import HuggingFaceCrossEncoder


# def get_reranker_model():
#     return HuggingFaceCrossEncoder(
#         model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
#     )



# from langchain_community.cross_encoders import HuggingFaceCrossEncoder


# def get_reranker_model():
#     return HuggingFaceCrossEncoder(
#         model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
#     )
