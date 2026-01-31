from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse

from customer.authentication import CustomerJWTAuthentication
from staff.authentication import StaffJWTAuthentication

from orders.models import Order
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer, SendMessageRequestSerializer
from .permissions import IsChatParticipant


def _chat_allowed(order: Order) -> bool:
    # pending => yo'q, canceled => yo'q
    if order.status == Order.Status.PENDING:
        return False
    if order.status == Order.Status.CANCELED:
        return False
    # accepted va undan keyin => bor
    return True


class ChatRoomListView(APIView):
    authentication_classes = [CustomerJWTAuthentication, StaffJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chat"],
        responses={200: ChatRoomSerializer(many=True)},
        description="Userga tegishli chat roomlar ro'yxati."
    )
    def get(self, request):
        if request.user.__class__.__name__ == "Customer":
            qs = ChatRoom.objects.select_related("customer", "staff", "order").filter(customer=request.user)
        elif request.user.__class__.__name__ == "Staff":
            qs = ChatRoom.objects.select_related("customer", "staff", "order").filter(staff=request.user)
        else:
            return Response({"detail": "Invalid user"}, status=403)

        # faqat chat allowed orderlar (accepted+)
        qs = [r for r in qs if _chat_allowed(r.order)]
        return Response(ChatRoomSerializer(qs, many=True).data, status=200)


class ChatMessageListView(APIView):
    authentication_classes = [CustomerJWTAuthentication, StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsChatParticipant]

    @extend_schema(
        tags=["chat"],
        responses={200: ChatMessageSerializer(many=True), 403: OpenApiResponse(description="Forbidden")},
        description="Tanlangan room ichidagi barcha xabarlar."
    )
    def get(self, request, room_id: int):
        room = get_object_or_404(ChatRoom.objects.select_related("order", "customer", "staff"), id=room_id)
        self.check_object_permissions(request, room)

        if not _chat_allowed(room.order):
            return Response({"detail": "Chat faqat order ACCEPTED bo'lgandan keyin ishlaydi."}, status=400)

        qs = ChatMessage.objects.filter(room=room).order_by("created_at")
        return Response(ChatMessageSerializer(qs, many=True).data, status=200)


class ChatSendMessageView(APIView):
    authentication_classes = [CustomerJWTAuthentication, StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsChatParticipant]

    @extend_schema(
        tags=["chat"],
        request=SendMessageRequestSerializer,
        responses={201: ChatMessageSerializer, 400: OpenApiResponse(description="Invalid")},
        description="Roomga yangi xabar yuborish (REST)."
    )
    def post(self, request, room_id: int):
        room = get_object_or_404(ChatRoom.objects.select_related("order", "customer", "staff"), id=room_id)
        self.check_object_permissions(request, room)

        if not _chat_allowed(room.order):
            return Response({"detail": "Chat faqat order ACCEPTED bo'lgandan keyin ishlaydi."}, status=400)

        ser = SendMessageRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        if request.user.__class__.__name__ == "Customer":
            msg = ChatMessage.objects.create(room=room, sender_customer=request.user, text=ser.validated_data["text"])
        else:
            msg = ChatMessage.objects.create(room=room, sender_staff=request.user, text=ser.validated_data["text"])

        # WS broadcast (REST orqali yuborilganda ham real-time)
        # optional: agar channel layer bo'lsa broadcast qilamiz
        try:
            from asgiref.sync import async_to_sync
            from chat.layers import get_channel_layer
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{room.id}",
                {
                    "type": "chat.message",
                    "message": {
                        "id": msg.id,
                        "text": msg.text,
                        "sender_type": msg.sender_type(),
                        "created_at": msg.created_at.isoformat(),
                    },
                },
            )
        except Exception:
            pass

        return Response(ChatMessageSerializer(msg).data, status=201)
