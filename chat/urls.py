from django.urls import path
from .views import ChatRoomListView, ChatMessageListView, ChatSendMessageView

urlpatterns = [
    path("chat/rooms/", ChatRoomListView.as_view()),
    path("chat/rooms/<int:room_id>/messages/", ChatMessageListView.as_view()),
    path("chat/rooms/<int:room_id>/send/", ChatSendMessageView.as_view()),
]
