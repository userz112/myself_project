from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.ChatView.as_view(), name="assistant-chat"),
    path("chat/stream/", views.ChatStreamView.as_view(), name="assistant-chat-stream"),
]
