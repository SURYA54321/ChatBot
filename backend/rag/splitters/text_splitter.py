import logging
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Splits loaded documents into smaller chunks for accurate vector embedding.
    Uses pure string operations (RecursiveCharacterTextSplitter) to avoid loading NLTK/Spacy.
    """
    try:
        # This splitter is lightweight and natively looks for paragraphs, sentences, then words.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Successfully split {len(documents)} docs into {len(chunks)} chunks.")
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error during document splitting: {str(e)}")
        raise e