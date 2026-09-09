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

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    # >>> NEW: ties every document to the exact chat it was uploaded in.
    # This is the core fix for cross-chat document leakage.
    conversation = models.ForeignKey(
        "conversations.Conversation",
        on_delete=models.CASCADE,
        related_name="documents",
    )

    name = models.CharField(
        max_length=255,
    )

    file = models.FileField(
        upload_to="documents/",
    )

    file_type = models.CharField(
        max_length=50,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        # >>> NEW: every document listing/lookup in the new flow is
        # scoped by conversation, so index it.
        indexes = [
            models.Index(fields=["conversation", "status"]),
        ]

    def __str__(self):
        return self.name