from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation
from .serializers import ConversationSerializer, MessageSerializer


class ConversationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(
            user=request.user
        )

        serializer = ConversationSerializer(
            conversations,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = ConversationSerializer(
            data=request.data
        )

        if serializer.is_valid():
            conversation = serializer.save(
                user=request.user
            )

            return Response(
                ConversationSerializer(conversation).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_conversation(self, request, conversation_id):
        return get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user,
        )

    def get(self, request, conversation_id):
        conversation = self.get_conversation(
            request,
            conversation_id,
        )

        serializer = ConversationSerializer(
            conversation
        )

        return Response(serializer.data)

    def patch(self, request, conversation_id):
        conversation = self.get_conversation(
            request,
            conversation_id,
        )

        serializer = ConversationSerializer(
            conversation,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, conversation_id):
        conversation = self.get_conversation(
            request,
            conversation_id,
        )

        conversation.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ConversationMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user,
        )

        messages = conversation.messages.all()

        serializer = MessageSerializer(
            messages,
            many=True,
        )

        return Response(serializer.data)
