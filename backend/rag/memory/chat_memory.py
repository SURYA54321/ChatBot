from conversations.models import Message


def get_recent_messages(
    conversation_id,
    max_messages: int = 20,
):
    """
    Return recent messages from a conversation.
    """

    messages = (
        Message.objects
        .filter(conversation_id=conversation_id)
        .order_by("-created_at")[:max_messages]
    )

    return list(reversed(messages))


def get_chat_history(
    conversation_id,
    max_messages: int = 20,
):
    """
    Return recent messages formatted as text.
    """

    messages = get_recent_messages(
        conversation_id,
        max_messages,
    )

    history = []

    for message in messages:
        role = message.role.capitalize()

        history.append(
            f"{role}: {message.content}"
        )

    return "\n".join(history)
