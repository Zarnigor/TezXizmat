import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import ChatRoom, ChatMessage
from orders.models import Order


def _chat_allowed_status(status: str) -> bool:
    if status == Order.Status.PENDING:
        return False
    if status == Order.Status.CANCELED:
        return False
    return True


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = int(self.scope["url_route"]["kwargs"]["room_id"])
        self.group_name = f"chat_{self.room_id}"

        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        room = await self._get_room()
        if room is None:
            await self.close(code=4004)
            return

        # participant check
        if user.__class__.__name__ == "Customer":
            if room.customer_id != user.id:
                await self.close(code=4003)
                return
        elif user.__class__.__name__ == "Staff":
            if room.staff_id != user.id:
                await self.close(code=4003)
                return
        else:
            await self.close(code=4003)
            return

        # status check
        if not _chat_allowed_status(room.order.status):
            await self.close(code=4000)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        except Exception:
            pass

    async def receive(self, text_data=None, bytes_data=None):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            return

        try:
            data = json.loads(text_data or "{}")
        except Exception:
            return

        text = (data.get("text") or "").strip()
        if not text:
            return

        room = await self._get_room()
        if room is None:
            return

        if not _chat_allowed_status(room.order.status):
            await self.send(text_data=json.dumps({"error": "Chat not allowed for this order status"}))
            return

        msg = await self._save_message(room_id=room.id, user=user, text=text)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": {
                    "id": msg["id"],
                    "text": msg["text"],
                    "sender_type": msg["sender_type"],
                    "created_at": msg["created_at"],
                },
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @sync_to_async
    def _get_room(self):
        return (
            ChatRoom.objects
            .select_related("order", "customer", "staff")
            .filter(id=self.room_id)
            .first()
        )

    @sync_to_async
    def _save_message(self, room_id: int, user, text: str):
        room = ChatRoom.objects.get(id=room_id)

        if user.__class__.__name__ == "Customer":
            m = ChatMessage.objects.create(room=room, sender_customer=user, text=text)
        else:
            m = ChatMessage.objects.create(room=room, sender_staff=user, text=text)

        return {
            "id": m.id,
            "text": m.text,
            "sender_type": m.sender_type(),
            "created_at": m.created_at.isoformat(),
        }
