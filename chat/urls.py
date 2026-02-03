from django.urls import path
from .views import ChatRoomListView, ChatMessageListView, ChatSendMessageView, RoomFindView, ChatDeleteView

urlpatterns = [
    path("chat/rooms/", ChatRoomListView.as_view()),
    path("chat/rooms/<int:room_id>/messages/", ChatMessageListView.as_view()),
    path("chat/rooms/<int:room_id>/send/", ChatSendMessageView.as_view()),
    path("rooms/find/", RoomFindView.as_view(), name="chat-room-find"),
    path("chat/<int:room_id>/delete/", ChatDeleteView.as_view()),
]
