import os

import django


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

django.setup()


from conversations.models import Conversation
from rag.memory.chat_memory import get_chat_history


conversation = Conversation.objects.first()


if not conversation:
    print("No conversation found.")
    print("Create a conversation first.")
else:
    history = get_chat_history(
        conversation_id=conversation.id,
    )

    print("CHAT HISTORY")
    print("=" * 60)
    print(history)
