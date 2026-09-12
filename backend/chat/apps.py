import os

from django.apps import AppConfig


class ChatConfig(AppConfig):
    name = 'chat'

    # def ready(self):
    #     # >>> FIXED: Django's runserver autoreloader spawns two
    #     # processes — a watcher process and the actual server
    #     # process. Without this check, ready() runs in BOTH,
    #     # loading the embedding model and reranker model twice
    #     # (this is the "model runs two times" issue flagged).
    #     #
    #     # RUN_MAIN is set to "true" only in the actual child server
    #     # process that Django's reloader spawns, not in the parent
    #     # watcher process. This is Django's own documented mechanism
    #     # for this exact problem.
    #     if os.environ.get("RUN_MAIN") != "true":
    #         return

    #     from rag.embeddings.embedding_model import get_embedding_model
    #     from rag.reranker.cross_encoder import get_reranker_model

    #     get_embedding_model()
    #     get_reranker_model()