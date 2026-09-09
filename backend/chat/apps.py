from django.apps import AppConfig

import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

class ChatConfig(AppConfig):
    name = 'chat'
    

    def ready(self):
        import torch
        import os

        torch.set_num_threads(os.cpu_count())
        print(f"🧵 PyTorch using {torch.get_num_threads()} threads")

        from rag.embeddings.embedding_model import get_embedding_model
        from rag.reranker.cross_encoder import get_reranker_model
        get_embedding_model()
        get_reranker_model()