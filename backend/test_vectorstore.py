from rag.ingestion import process_document
from Pre_project.backend.rag.vectorstore.simple_store import add_documents


file_path = "test_document.txt"

chunks = process_document(
    file_path=file_path,
    user_id="test-user-1",
    document_id="test-document-1",
    filename="test_document.txt",
    file_type="txt",
)

print(f"Chunks created: {len(chunks)}")

for chunk in chunks:
    print("\nMetadata:")
    print(chunk.metadata)


ids = add_documents(chunks)

print(f"\nVectors added: {len(ids)}")
print("Vector store is working!")
