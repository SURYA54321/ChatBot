from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "name",
            "file",
            "file_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "name",
            "file_type",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_file(self, file):
        max_size = 10 * 1024 * 1024  # 10 MB

        if file.size > max_size:
            raise serializers.ValidationError(
                "File size cannot exceed 10 MB."
            )

        allowed_extensions = {
            ".pdf",
            ".txt",
            ".docx",
            ".md",
            ".csv",
        }

        file_name = file.name.lower()

        if not any(
            file_name.endswith(extension)
            for extension in allowed_extensions
        ):
            raise serializers.ValidationError(
                "Unsupported file type."
            )

        return file
