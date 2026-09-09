from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from rag.ingestion import process_document
from rag.vectorstore.chroma_store import add_documents

from .models import Document
from .serializers import DocumentSerializer

from rag.vectorstore.chroma_store import (
    delete_document_vectors,
)

class DocumentListUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        documents = Document.objects.filter(
            user=request.user
        )

        serializer = DocumentSerializer(
            documents,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        print("CONTENT TYPE:", request.content_type)
        print("DATA:", request.data)
        print("FILES:", request.FILES)
        serializer = DocumentSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        document = serializer.save(
            user=request.user,
            name=serializer.validated_data["file"].name,
            file_type=serializer.validated_data[
                "file"
            ].name.split(".")[-1].lower(),
        )

        # --------------------------------------------
        # Start processing
        # --------------------------------------------

        document.status = "processing"
        document.save(
            update_fields=["status"]
        )

        try:
            chunks = process_document(
                file_path=document.file.path,
                user_id=str(request.user.id),
                document_id=str(document.id),
                filename=document.name,
                file_type=document.file_type,
            )

            if not chunks:
                raise ValueError(
                    "No text could be extracted from the document."
                )

            add_documents(chunks)

            document.status = "completed"
            document.save(
                update_fields=["status"]
            )

        except Exception:
            document.status = "failed"
            document.save(
                update_fields=["status"]
            )

            return Response(
                {
                    "detail": "Document processing failed.",
                    "document": DocumentSerializer(
                        document
                    ).data,
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
            return Document.objects.get(
                id=document_id,
                user=request.user,
            )
        except Document.DoesNotExist:
            return None

    def get(self, request, document_id):
        document = self.get_object(
            request,
            document_id,
        )

        if not document:
            return Response(
                {"detail": "Document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DocumentSerializer(document)

        return Response(serializer.data)

    def delete(self, request, document_id):
     document = self.get_object(
        request,
        document_id,
     )

     if not document:
        return Response(
            {"detail": "Document not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

     delete_document_vectors(
        document_id=str(document.id),
        user_id=str(request.user.id),
     )

     document.file.delete(save=False)
     document.delete()

     return Response(
        status=status.HTTP_204_NO_CONTENT
     )