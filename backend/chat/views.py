from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from conversations.models import Conversation, Message
from rag.memory.chat_memory import get_chat_history
from rag.pipeline import run_rag

from .serializers import ChatRequestSerializer
from rag.sources.source_formatter import format_sources
from django.http import StreamingHttpResponse
import json

from django.http import StreamingHttpResponse

from rag.pipeline import stream_rag
from rag.sources.source_formatter import format_sources

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation_id = serializer.validated_data["conversation_id"]
        message_text = serializer.validated_data["message"]

        # --------------------------------------------------
        # 1. Get user's conversation
        # --------------------------------------------------

        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user=request.user,
            )
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # --------------------------------------------------
        # 2. Get previous conversation history
        # --------------------------------------------------

        chat_history = get_chat_history(
            conversation_id=conversation.id,
            max_messages=20,
        )

        # --------------------------------------------------
        # 3. Save user message
        # --------------------------------------------------

        user_message = Message.objects.create(
            conversation=conversation,
            role="user",
            content=message_text,
        )

        # --------------------------------------------------
        # 4. Run RAG
        # --------------------------------------------------

        try:
            result = run_rag(
                question=message_text,
                user_id=str(request.user.id),
                chat_history=chat_history,
            )
        except Exception:
            return Response(
                {"detail": "Failed to generate a response."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # --------------------------------------------------
        # 5. Save assistant response
        # --------------------------------------------------

        assistant_message = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=result["answer"],
        )

        conversation.save(
            update_fields=["updated_at"]
        )

        # --------------------------------------------------
        # 6. Build sources
        # --------------------------------------------------

        sources = []

        sources = format_sources(
        result["documents"]
    )


        # --------------------------------------------------
        # 7. Return response
        # --------------------------------------------------

        return Response(
            {
                "conversation_id": str(
                    conversation.id
                ),

                "user_message": {
                    "id": str(user_message.id),
                    "role": user_message.role,
                    "content": user_message.content,
                    "created_at": user_message.created_at,
                },

                "assistant_message": {
                    "id": str(assistant_message.id),
                    "role": assistant_message.role,
                    "content": assistant_message.content,
                    "created_at": assistant_message.created_at,
                },

                "answer": result["answer"],

                "rewritten_query": result[
                    "rewritten_query"
                ],

                "sources": sources,
            },
            status=status.HTTP_200_OK,
        )

class ChatStreamView(APIView):

    def post(self, request):
        serializer = ChatRequestSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        conversation_id = serializer.validated_data[
            "conversation_id"
        ]

        message_text = serializer.validated_data[
            "message"
        ]

        # --------------------------------------------
        # 1. Verify conversation ownership
        # --------------------------------------------

        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user=request.user,
            )
        except Conversation.DoesNotExist:
            return Response(
                {
                    "detail": "Conversation not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # --------------------------------------------
        # 2. Get conversation history
        # --------------------------------------------

        chat_history = get_chat_history(
            conversation_id=conversation.id,
            max_messages=20,
        )

        # --------------------------------------------
        # 3. Save user message
        # --------------------------------------------

        user_message = Message.objects.create(
            conversation=conversation,
            role="user",
            content=message_text,
        )

        # --------------------------------------------
        # 4. Generator
        # --------------------------------------------

        def generate():

            full_answer = ""
            rewritten_query = ""
            documents = []

            try:

                for event in stream_rag(
                    question=message_text,
                    user_id=str(request.user.id),
                    chat_history=chat_history,
                ):

                    # ------------------------------
                    # Token
                    # ------------------------------

                    if event["type"] == "token":

                        content = event["content"]

                        full_answer += content

                        yield (
                            f"data: {json.dumps({
                                'type': 'token',
                                'content': content,
                            })}\n\n"
                        )

                    # ------------------------------
                    # Retrieval complete
                    # ------------------------------

                    elif event["type"] == "done":

                        rewritten_query = event[
                            "rewritten_query"
                        ]

                        documents = event[
                            "documents"
                        ]

                # ----------------------------------
                # Save assistant response
                # ----------------------------------

                assistant_message = Message.objects.create(
                    conversation=conversation,
                    role="assistant",
                    content=full_answer,
                )

                conversation.save(
                    update_fields=["updated_at"]
                )

                # ----------------------------------
                # Format sources
                # ----------------------------------

                sources = format_sources(
                    documents
                )

                # ----------------------------------
                # Final SSE event
                # ----------------------------------

                yield (
                    f"data: {json.dumps({
                        'type': 'done',
                        'message_id': str(
                            assistant_message.id
                        ),
                        'rewritten_query': rewritten_query,
                        'sources': sources,
                    })}\n\n"
                )

            except Exception as error:

                print(
                    "STREAMING ERROR:",
                    repr(error)
                )

                yield (
                    f"data: {json.dumps({
                        'type': 'error',
                        'message': (
                            'Failed to generate response.'
                        ),
                    })}\n\n"
                )

        # --------------------------------------------
        # 5. Streaming response
        # --------------------------------------------

        response = StreamingHttpResponse(
            generate(),
            content_type="text/event-stream",
        )

        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"

        return response
