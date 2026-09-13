import uuid

from django.conf import settings
from django.db import models


class Document(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents")
    conversation = models.ForeignKey("conversations.Conversation", on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    file_type = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["conversation", "status"])]

    def __str__(self):
        return self.name


class DocumentChunk(models.Model):
    """
    >>> NEW: replaces Chroma entirely. Stores each chunk's text and
    its embedding vector directly in the database. Retrieval does
    plain cosine similarity in Python/NumPy over the (small) set of
    chunks scoped to one user+conversation — no vector database
    needed at this scale (a handful of documents per chat).

    This removes chromadb and its heavy unused transitive
    dependencies (grpcio, a full kubernetes client, onnxruntime,
    OpenTelemetry's gRPC exporter) from the app's memory footprint
    entirely.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    # Denormalized user/conversation so retrieval can filter directly
    # without joining through document -> conversation each query.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="document_chunks")
    conversation = models.ForeignKey("conversations.Conversation", on_delete=models.CASCADE, related_name="document_chunks")
    chunk_index = models.IntegerField(default=0)
    content = models.TextField()
    embedding = models.JSONField()
    filename = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    page = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user", "conversation"])]

    def __str__(self):
        return f"{self.filename} chunk {self.chunk_index}"