from django.urls import path

from .views import (
    DocumentDetailView,
    DocumentListUploadView,
)


urlpatterns = [
    path(
        "",
        DocumentListUploadView.as_view(),
        name="document-list-upload",
    ),

    path(
        "<uuid:document_id>/",
        DocumentDetailView.as_view(),
        name="document-detail",
    ),
]