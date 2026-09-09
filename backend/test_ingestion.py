from rag.ingestion import process_document


file_path = "test_document.txt"

chunks = process_document(file_path)

print(f"Total chunks: {len(chunks)}")

for index, chunk in enumerate(chunks):
    print("\n" + "=" * 60)
    print(f"CHUNK {index + 1}")
    print("=" * 60)

    print(chunk.page_content)

    print("\nMETADATA:")
    print(chunk.metadata)
