# Gemini New

import logging
import os
from typing import List

import fitz  # PyMuPDF
from django.db import transaction
from google import genai
from google.genai import types
from langchain_core.documents import Document

from documents.models import DocumentChunk
from rag.embeddings.embedding_model import get_embedding_model
from rag.loaders.document_loader import load_document

# Handles both import path structures safely
try:
    from rag.loaders.text_splitter import split_documents
except ImportError:
    from rag.splitters.text_splitter import split_documents

logger = logging.getLogger(__name__)


def _extract_ocr_documents(file_path: str) -> List[Document]:
    """
    Renders PDF/image pages into in-memory JPEG bytes via PyMuPDF 
    and sends them to Gemini Vision API for high-accuracy OCR.
    Runs entirely in RAM (< 100 MB overhead) without requiring Poppler or Tesseract binaries.
    """
    logger.info("Falling back to Gemini Vision OCR for file: %s", file_path)
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY / GOOGLE_API_KEY not configured in environment.")
        return []

    client = genai.Client(api_key=api_key)
    ocr_documents: List[Document] = []

    try:
        # PyMuPDF seamlessly opens PDFs and raw image files (PNG, JPG, JPEG, TIFF, WebP)
        doc = fitz.open(file_path)

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Render page to JPEG bytes in memory (150 DPI is optimal for fast OCR)
            pix = page.get_pixmap(dpi=150)
            image_bytes = pix.tobytes("jpeg")

            prompt = (
                "Extract and transcribe all text, tables, and structured data visible on "
                "this page verbatim. Do not summarize or add conversational commentary."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt,
                ],
            )

            extracted_text = response.text.strip() if response.text else ""

            if extracted_text:
                ocr_documents.append(
                    Document(
                        page_content=f"--- Page {page_num + 1} (OCR) ---\n{extracted_text}",
                        metadata={"page": page_num + 1, "ocr": True},
                    )
                )

        doc.close()
        logger.info(
            "Gemini Vision OCR successfully extracted text from %d page(s) for %s",
            len(ocr_documents),
            file_path,
        )

    except Exception as e:
        logger.error("Gemini Vision OCR extraction failed for %s: %s", file_path, str(e))

    return ocr_documents


def process_document(
    file_path: str,
    user_id: str,
    conversation_id: str,
    document_id: str,
    filename: str,
    file_type: str,
) -> List:
    """
    Loads, splits, generates embeddings, and stores document chunks in SQLite.
    Includes automated Gemini Flash Vision OCR fallback for scanned/image PDFs.
    """
    try:
        # Step 1: Load file content using lightweight parsers (PyMuPDF / Docx2txt)
        documents = load_document(file_path)
        
        # Measure extracted text volume to detect image-only / scanned documents
        total_text = " ".join([doc.page_content for doc in documents]).strip() if documents else ""

        # Step 2: Fall back to Gemini Vision OCR if standard text parsing returns empty / minimal text (< 10 words)
        if not documents or len(total_text.split()) < 10:
            logger.warning(
                "No readable plain text found in %s (found %d words). Triggering Gemini Vision OCR...",
                file_path,
                len(total_text.split()),
            )
            ocr_docs = _extract_ocr_documents(file_path)
            if ocr_docs:
                documents = ocr_docs
            else:
                logger.warning("No content could be extracted from file even after OCR fallback: %s", file_path)
                return []

        # Step 3: Split content into text chunks
        chunks = split_documents(documents)
        if not chunks:
            logger.warning("No chunks generated for file: %s", file_path)
            return []

        # Step 4: Enrich chunk metadata and extract raw texts
        chunk_texts = []
        for index, chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    "user_id": str(user_id),
                    "conversation_id": str(conversation_id),
                    "document_id": str(document_id),
                    "filename": filename,
                    "file_type": file_type,
                    "chunk_index": index,
                    "source": filename,
                }
            )
            chunk_texts.append(chunk.page_content)

        # Step 5: Generate vector embeddings remotely via HF API (0 MB local PyTorch RAM)
        embedding_model = get_embedding_model()
        embeddings = embedding_model.embed_documents(chunk_texts)

        # Step 6: Save chunks atomically to SQLite DocumentChunk table
        with transaction.atomic():
            # Remove pre-existing chunks for this document if re-ingesting
            DocumentChunk.objects.filter(document_id=document_id).delete()

            db_chunks = []
            for index, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                page_num = chunk.metadata.get("page", None)

                db_chunk = DocumentChunk(
                    document_id=document_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    chunk_index=index,
                    content=chunk.page_content,
                    embedding=vector,  # Native Python float list saved directly into JSONField
                    filename=filename,
                    file_type=file_type,
                    page=page_num if isinstance(page_num, int) else None,
                )
                db_chunks.append(db_chunk)

            DocumentChunk.objects.bulk_create(db_chunks)

        logger.info(
            "Successfully ingested %d chunks into SQLite for document %s.",
            len(db_chunks),
            document_id,
        )
        return chunks

    except Exception as e:
        logger.error("Error processing document %s: %s", document_id, str(e))
        raise e

# import logging
# from typing import List
# from django.db import transaction

# from documents.models import DocumentChunk
# from rag.loaders.document_loader import load_document
# from rag.embeddings.embedding_model import get_embedding_model

# # Handles both import path structures safely
# try:
#     from rag.loaders.text_splitter import split_documents
# except ImportError:
#     from rag.splitters.text_splitter import split_documents

# logger = logging.getLogger(__name__)


# def process_document(
#     file_path: str,
#     user_id: str,
#     conversation_id: str,
#     document_id: str,
#     filename: str,
#     file_type: str,
# ) -> List:
#     """
#     Load, split, generate remote embeddings via Hugging Face API, 
#     and store document chunks directly into SQLite for lightweight RAG.
#     """
#     try:
#         # Step 1: Load file content using lightweight parsers (PyMuPDF / Docx2txt)
#         documents = load_document(file_path)
#         if not documents:
#             logger.warning(f"No content extracted from file: {file_path}")
#             return []

#         # Step 2: Split content into text chunks
#         chunks = split_documents(documents)
#         if not chunks:
#             logger.warning(f"No chunks generated for file: {file_path}")
#             return []

#         # Step 3: Enrich chunk metadata and extract raw texts
#         chunk_texts = []
#         for index, chunk in enumerate(chunks):
#             chunk.metadata.update(
#                 {
#                     "user_id": str(user_id),
#                     "conversation_id": str(conversation_id),
#                     "document_id": str(document_id),
#                     "filename": filename,
#                     "file_type": file_type,
#                     "chunk_index": index,
#                     "source": filename,
#                 }
#             )
#             chunk_texts.append(chunk.page_content)

#         # Step 4: Generate vector embeddings remotely via HF API (0 MB local PyTorch RAM)
#         embedding_model = get_embedding_model()
#         embeddings = embedding_model.embed_documents(chunk_texts)

#         # Step 5: Save chunks atomically to SQLite DocumentChunk table
#         with transaction.atomic():
#             # Remove pre-existing chunks for this document if re-ingesting
#             DocumentChunk.objects.filter(document_id=document_id).delete()

#             db_chunks = []
#             for index, (chunk, vector) in enumerate(zip(chunks, embeddings)):
#                 page_num = chunk.metadata.get("page", None)

#                 db_chunk = DocumentChunk(
#                     document_id=document_id,
#                     user_id=user_id,
#                     conversation_id=conversation_id,
#                     chunk_index=index,
#                     content=chunk.page_content,
#                     embedding=vector,  # Native Python float list saved directly into JSONField
#                     filename=filename,
#                     file_type=file_type,
#                     page=page_num if isinstance(page_num, int) else None,
#                 )
#                 db_chunks.append(db_chunk)

#             DocumentChunk.objects.bulk_create(db_chunks)

#         logger.info(
#             f"Successfully ingested {len(db_chunks)} chunks into SQLite for document {document_id}."
#         )
#         return chunks

#     except Exception as e:
#         logger.error(f"Error processing document {document_id}: {str(e)}")
#         raise e