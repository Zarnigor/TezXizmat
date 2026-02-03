from django.urls import path
from .views import (
    ChatRoomListView,
    ChatRoomMessagesView,
    ChatRoomSendMessageView,
    ChatRoomDeleteView,
    ChatRoomFindView, ChatRoomCreateView,
)

urlpatterns = [
    path("chat/rooms/", ChatRoomListView.as_view()),
    path("chat/rooms/<int:room_id>/messages/", ChatRoomMessagesView.as_view()),
    path("chat/rooms/<int:room_id>/send/", ChatRoomSendMessageView.as_view()),
    path("chat/<int:room_id>/delete/", ChatRoomDeleteView.as_view()),
    path("chat/rooms/find/", ChatRoomFindView.as_view()),
    path("chat/rooms/create/", ChatRoomCreateView.as_view()),
]
