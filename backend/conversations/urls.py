from django.urls import path

from .views import (
    ConversationDetailView,
    ConversationListCreateView,
    ConversationMessagesView,
)


urlpatterns = [
    path(
        "",
        ConversationListCreateView.as_view(),
        name="conversation-list-create",
    ),

    path(
        "<uuid:conversation_id>/",
        ConversationDetailView.as_view(),
        name="conversation-detail",
    ),

    path(
        "<uuid:conversation_id>/messages/",
        ConversationMessagesView.as_view(),
        name="conversation-messages",
    ),
]
