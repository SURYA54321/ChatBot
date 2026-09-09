from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField()

    message = serializers.CharField(
        max_length=10000,
        allow_blank=False,
        trim_whitespace=True,
    )
