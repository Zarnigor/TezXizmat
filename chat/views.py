from customer.authentication import CustomerJWTAuthentication
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from orders.models import Order
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from staff.authentication import StaffJWTAuthentication

from .models import ChatRoom, ChatMessage
from .permissions import IsChatParticipant
from .serializers import ChatRoomSerializer, ChatMessageSerializer, SendMessageRequestSerializer
from .serializers import RoomFindRequestSerializer, RoomFindResponseSerializer


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



class RoomFindView(APIView):
    permission_classes = [AllowAny]  # keyin token bilan yopamiz

    @extend_schema(
        tags=["chat"],
        request=RoomFindRequestSerializer,
        responses={
            200: RoomFindResponseSerializer,
            404: OpenApiResponse(description="Room not found"),
        },
        description="customer_id va staff_id bo‘yicha mavjud roomni topib room_id qaytaradi."
    )
    def post(self, request):
        ser = RoomFindRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        customer_id = ser.validated_data["customer_id"]
        staff_id = ser.validated_data["staff_id"]

        room = (
            ChatRoom.objects
            .filter(customer_id=customer_id, staff_id=staff_id)
            .order_by("-created_at")
            .first()
        )

        if not room:
            return Response({"detail": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"room_id": room.id}, status=status.HTTP_200_OK)
