import os
from langchain_huggingface import HuggingFaceEndpointEmbeddings


def get_embedding_model():
    """
    Returns HuggingFace Remote Endpoint Embeddings.
    Offloads vector calculation to HuggingFace API so local PyTorch 
    is never loaded into server RAM.
    """
    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")

    if not hf_token:
        raise ValueError(
            "Missing HUGGINGFACEHUB_API_TOKEN environment variable. "
            "Set it in your environment or Render settings."
        )

    return HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        huggingfacehub_api_token=hf_token,
    )