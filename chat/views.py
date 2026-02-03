from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import ChatRoom, ChatMessage
from .serializers import (
    ChatRoomOutSerializer,
    ChatRoomCreateInSerializer,
    ChatMessageOutSerializer,
    ChatMessageSendInSerializer,
)

# Sizda mavjud bo‘lsa shularni qo‘ying:
# from your_project.auth import CustomerJWTAuthentication, StaffJWTAuthentication


def _user_type(user):
    n = user.__class__.__name__
    if n == "Customer":
        return "customer"
    if n == "Staff":
        return "staff"
    return None


def _check_room_participant_or_403(request, room: ChatRoom):
    ut = _user_type(request.user)
    if ut == "customer" and room.customer_id != request.user.id:
        return False
    if ut == "staff" and room.staff_id != request.user.id:
        return False
    return ut is not None


# -------------------------------------------------
# POST /api/chat/rooms/create/
# -------------------------------------------------
class ChatRoomCreateView(APIView):
    authentication_classes = []  # [CustomerJWTAuthentication, StaffJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chat"],
        request=ChatRoomCreateInSerializer,
        responses={
            200: ChatRoomOutSerializer,
            201: ChatRoomOutSerializer,
            400: OpenApiResponse(description="Invalid input"),
            403: OpenApiResponse(description="Invalid user"),
        },
        description="Chat room yaratadi yoki mavjud bo‘lsa qaytaradi (customer+staff unique).",
    )
    def post(self, request):
        ut = _user_type(request.user)
        if ut is None:
            return Response({"detail": "Invalid user"}, status=403)

        inp = ChatRoomCreateInSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        order_id = inp.validated_data.get("order_id")

        if ut == "customer":
            staff_id = inp.validated_data.get("staff_id")
            if not staff_id:
                return Response({"detail": "staff_id required"}, status=400)

            room, created = ChatRoom.objects.get_or_create(
                customer=request.user,
                staff_id=staff_id,
                defaults={"order_id": order_id} if order_id else {},
            )
        else:
            customer_id = inp.validated_data.get("customer_id")
            if not customer_id:
                return Response({"detail": "customer_id required"}, status=400)

            room, created = ChatRoom.objects.get_or_create(
                staff=request.user,
                customer_id=customer_id,
                defaults={"order_id": order_id} if order_id else {},
            )

        # optional: kelgan order_id ni set qilish
        if order_id and room.order_id is None:
            room.order_id = order_id
            room.save(update_fields=["order"])

        # Agar user o'zidan delete qilgan bo'lsa, create qilganda "restore" bo'lsin
        if ut == "customer" and room.deleted_by_customer:
            room.deleted_by_customer = False
            room.save(update_fields=["deleted_by_customer"])
        if ut == "staff" and room.deleted_by_staff:
            room.deleted_by_staff = False
            room.save(update_fields=["deleted_by_staff"])

        room._last_message_cache = room.messages.order_by("-created_at").first()

        status_code = 201 if created else 200
        return Response(
            ChatRoomOutSerializer(room, context={"request": request}).data,
            status=status_code,
        )


# -------------------------------------------------
# POST /api/rooms/find/   (eski endpoint qoladi)
# -------------------------------------------------
class ChatRoomFindView(APIView):
    authentication_classes = []  # [CustomerJWTAuthentication, StaffJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chat"],
        request=ChatRoomCreateInSerializer,
        responses={200: ChatRoomOutSerializer, 201: ChatRoomOutSerializer},
        description="create endpoint bilan bir xil: room topadi yoki yaratadi.",
    )
    def post(self, request):
        # ichida aynan create view logikasi
        return ChatRoomCreateView().post(request)


# -------------------------------------------------
# GET /api/chat/rooms/
# -------------------------------------------------
class ChatRoomListView(APIView):
    authentication_classes = []  # [CustomerJWTAuthentication, StaffJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chat"],
        responses={200: ChatRoomOutSerializer(many=True)},
        description="Userga tegishli chat roomlar (last_message, unread count bilan).",
    )
    def get(self, request):
        ut = _user_type(request.user)
        if ut == "customer":
            qs = (
                ChatRoom.objects
                .select_related("customer", "staff")
                .filter(customer=request.user, deleted_by_customer=False)
            )
        elif ut == "staff":
            qs = (
                ChatRoom.objects
                .select_related("customer", "staff")
                .filter(staff=request.user, deleted_by_staff=False)
            )
        else:
            return Response({"detail": "Invalid user"}, status=403)

        rooms = list(qs.order_by("-created_at"))

        # last_message cache (N+1 bo'ladi, lekin sodda; keyin optimize qilamiz)
        for r in rooms:
            r._last_message_cache = r.messages.order_by("-created_at").first()

        return Response(
            ChatRoomOutSerializer(rooms, many=True, context={"request": request}).data,
            status=200,
        )


# -------------------------------------------------
# GET /api/chat/rooms/{room_id}/messages/
# (bu chaqirilganda last_read_at update qilamiz)
# -------------------------------------------------
class ChatRoomMessagesView(APIView):
    authentication_classes = []  # [CustomerJWTAuthentication, StaffJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chat"],
        responses={200: ChatMessageOutSerializer(many=True)},
        description="Roomdagi message'lar ro'yxati. GET bo‘lganda 'read' qilib qo‘yadi.",
    )
    def get(self, request, room_id: int):
        room = get_object_or_404(ChatRoom.objects.select_related("customer", "staff"), id=room_id)

        if not _check_room_participant_or_403(request, room):
            return Response({"detail": "Forbidden"}, status=403)

        msgs = room.messages.all().order_by("created_at")

        # read time update
        now = timezone.now()
        ut = _user_type(request.user)
        if ut == "customer":
            ChatRoom.objects.filter(id=room.id).update(customer_last_read_at=now)
        elif ut == "staff":
            ChatRoom.objects.filter(id=room.id).update(staff_last_read_at=now)

        return Response(ChatMessageOutSerializer(msgs, many=True).data, status=200)


# -------------------------------------------------
# POST /api/chat/rooms/{room_id}/send/
# -------------------------------------------------
class ChatRoomSendMessageView(APIView):
    authentication_classes = []  # [CustomerJWTAuthentication, StaffJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chat"],
        request=ChatMessageSendInSerializer,
        responses={201: ChatMessageOutSerializer},
        description="Roomga message yuborish.",
    )
    def post(self, request, room_id: int):
        room = get_object_or_404(ChatRoom.objects.select_related("customer", "staff"), id=room_id)

        if not _check_room_participant_or_403(request, room):
            return Response({"detail": "Forbidden"}, status=403)

        inp = ChatMessageSendInSerializer(data=request.data)
        inp.is_valid(raise_exception=True)

        ut = _user_type(request.user)
        create_kwargs = {"room": room, "text": inp.validated_data["text"]}

        if ut == "customer":
            create_kwargs["sender_customer"] = request.user
        elif ut == "staff":
            create_kwargs["sender_staff"] = request.user
        else:
            return Response({"detail": "Invalid user"}, status=403)

        msg = ChatMessage.objects.create(**create_kwargs)

        # sender o'zini read qilib qo'ysin
        now = timezone.now()
        if ut == "customer":
            ChatRoom.objects.filter(id=room.id).update(customer_last_read_at=now)
        else:
            ChatRoom.objects.filter(id=room.id).update(staff_last_read_at=now)

        return Response(ChatMessageOutSerializer(msg).data, status=201)


# -------------------------------------------------
# DELETE /api/chat/{room_id}/delete/
# (faqat o'zidan o'chiradi, ikkovi ham o'chirsa dbdan delete)
# -------------------------------------------------
class ChatRoomDeleteView(APIView):
    authentication_classes = []  # [CustomerJWTAuthentication, StaffJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chat"],
        responses={204: OpenApiResponse(description="Deleted")},
        description="Chatni faqat o'zidan o‘chiradi (soft). Ikkalasi ham o‘chirsa room dbdan o‘chadi.",
    )
    def delete(self, request, room_id: int):
        room = get_object_or_404(ChatRoom, id=room_id)
        ut = _user_type(request.user)

        if ut == "customer":
            if room.customer_id != request.user.id:
                return Response({"detail": "Forbidden"}, status=403)
            room.deleted_by_customer = True
            room.save(update_fields=["deleted_by_customer"])

        elif ut == "staff":
            if room.staff_id != request.user.id:
                return Response({"detail": "Forbidden"}, status=403)
            room.deleted_by_staff = True
            room.save(update_fields=["deleted_by_staff"])

        else:
            return Response({"detail": "Invalid user"}, status=403)

        if room.deleted_by_customer and room.deleted_by_staff:
            room.delete()

        return Response(status=204)
