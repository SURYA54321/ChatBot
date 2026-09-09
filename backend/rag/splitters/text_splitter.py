from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):
    """
    Split loaded documents into smaller chunks
    suitable for embedding and vector retrieval.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    return text_splitter.split_documents(documents)
