import logging

from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from conversations.models import Conversation
from rag.ingestion import process_document
from rag.vectorstore.simple_store import (
    add_documents,
    delete_document_vectors,
)

from .models import Document
from .serializers import DocumentSerializer

logger = logging.getLogger(__name__)


class DocumentListUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        conversation_id = request.query_params.get("conversation_id")

        if not conversation_id:
            return Response(
                {"detail": "conversation_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        documents = Document.objects.filter(
            user=request.user,
            conversation_id=conversation_id,
        )

        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DocumentSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["file"]

        document = serializer.save(
            user=request.user,
            name=uploaded_file.name,
            file_type=uploaded_file.name.split(".")[-1].lower(),
        )

        document.status = "processing"
        document.save(update_fields=["status"])

        try:
            chunks = process_document(
                file_path=document.file.path,
                user_id=str(request.user.id),
                conversation_id=str(document.conversation_id),
                document_id=str(document.id),
                filename=document.name,
                file_type=document.file_type,
            )

            if not chunks:
                raise ValueError("No text could be extracted from the document.")

            add_documents(chunks)

            document.status = "completed"
            document.save(update_fields=["status"])

        except Exception:
            logger.exception(
                "Document processing failed for document_id=%s",
                document.id,
            )

            document.status = "failed"
            document.save(update_fields=["status"])

            return Response(
                {
                    "detail": "Document processing failed.",
                    "document": DocumentSerializer(document).data,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_201_CREATED,
        )


class DocumentDetailView(APIView):

    def get_object(self, request, document_id):
        try:
            return Document.objects.get(id=document_id, user=request.user)
        except Document.DoesNotExist:
            return None

    def get(self, request, document_id):
        document = self.get_object(request, document_id)

        if not document:
            return Response(
                {"detail": "Document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DocumentSerializer(document)
        return Response(serializer.data)

    def delete(self, request, document_id):
        document = self.get_object(request, document_id)

        if not document:
            return Response(
                {"detail": "Document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            delete_document_vectors(
                document_id=str(document.id),
                user_id=str(request.user.id),
            )
        except Exception:
            logger.exception(
                "Failed to delete chunks for document_id=%s",
                document.id,
            )

        document.file.delete(save=False)
        document.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)