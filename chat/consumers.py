import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import ChatRoom, ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = int(self.scope["url_route"]["kwargs"]["room_id"])
        self.group_name = f"chat_{self.room_id}"

        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4001)  # unauthorized
            return

        room = await self._get_room()
        if room is None:
            await self.close(code=4004)  # room not found
            return

        # participant check + deleted flag check
        user_type = user.__class__.__name__
        if user_type == "Customer":
            if room.customer_id != user.id:
                await self.close(code=4003)  # forbidden
                return
            if room.deleted_by_customer:
                await self.close(code=4005)  # room hidden for customer
                return

        elif user_type == "Staff":
            if room.staff_id != user.id:
                await self.close(code=4003)
                return
            if room.deleted_by_staff:
                await self.close(code=4005)  # room hidden for staff
                return
        else:
            await self.close(code=4003)
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

        # participant check (receive paytida ham)
        user_type = user.__class__.__name__
        if user_type == "Customer":
            if room.customer_id != user.id or room.deleted_by_customer:
                return
        elif user_type == "Staff":
            if room.staff_id != user.id or room.deleted_by_staff:
                return
        else:
            return

        msg = await self._save_message(room_id=room.id, user=user, text=text)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": msg,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    # -------------------------
    # DB helpers
    # -------------------------
    @sync_to_async
    def _get_room(self):
        # order endi optional, shuning uchun select_related("order") majburiy emas
        return (
            ChatRoom.objects
            .select_related("customer", "staff")
            .filter(id=self.room_id)
            .first()
        )

    @sync_to_async
    def _save_message(self, room_id: int, user, text: str):
        room = ChatRoom.objects.get(id=room_id)

        if user.__class__.__name__ == "Customer":
            m = ChatMessage.objects.create(room=room, sender_customer=user, text=text)
            # sender o'zini read deb belgilab qo'yamiz (unread count to'g'ri chiqishi uchun)
            ChatRoom.objects.filter(id=room.id).update(customer_last_read_at=m.created_at)
        else:
            m = ChatMessage.objects.create(room=room, sender_staff=user, text=text)
            ChatRoom.objects.filter(id=room.id).update(staff_last_read_at=m.created_at)

        # sender_type endi sizda @property bo'lsa -> m.sender_type
        sender_type = m.sender_type if hasattr(m, "sender_type") else None

        return {
            "id": m.id,
            "text": m.text,
            "sender_type": sender_type,
            "created_at": m.created_at.isoformat(),
        }
