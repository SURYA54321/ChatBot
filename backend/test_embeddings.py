from rag.embeddings.embedding_model import get_embedding_model


embedding_model = get_embedding_model()

text = "Django is a Python web framework."

vector = embedding_model.embed_query(text)

print("Embedding created successfully!")
print("Vector type:", type(vector))
print("Vector dimensions:", len(vector))
print("First 10 values:", vector[:10])
