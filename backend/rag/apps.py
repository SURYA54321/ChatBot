# from django.apps import AppConfig


# class RagConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'rag'
    
#     def ready(self):
#         """
#         Pre-load models when Django starts
#         """
#         print("🔥 Pre-warming RAG models...")
        
#         from rag.embeddings.embedding_model import get_embedding_model
#         from rag.reranker.cross_encoder import get_reranker_model
#         from rag.vectorstore.chroma_store import get_vector_store
        
#         # Load embedding model
#         get_embedding_model()
#         print("✅ Embedding model loaded")
        
#         # Load reranker model
#         get_reranker_model()
#         print("✅ Reranker model loaded")
        
#         # Initialize vector store
#         get_vector_store()
#         print("✅ Vector store connected")
        
#         print("🚀 RAG models ready!")