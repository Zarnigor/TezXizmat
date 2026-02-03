from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from orders.serializers import CustomerPublicOutSerializer, StaffPublicOutSerializer
from .models import ChatRoom, ChatMessage


class ChatRoomSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ("id", "order_id", "created_at", "customer", "staff")

    @extend_schema_field(CustomerPublicOutSerializer)
    def get_customer(self, obj):
        c = obj.customer
        return {
            "id": c.id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "image": c.image.url if getattr(c, "image", None) else None,
        }

    @extend_schema_field(StaffPublicOutSerializer)
    def get_staff(self, obj):
        s = obj.staff
        return {
            "id": s.id,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "image": s.image.url if getattr(s, "image", None) else None,
            "profession": s.profession,
            "description": s.description,
            "skills_text": s.skills_text,
            "price_text": s.price_text,
            "free_time_text": s.free_time_text,
        }


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_type = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ("id", "text", "sender_type", "created_at")

    def get_sender_type(self, obj):
        return obj.sender_type()


class SendMessageRequestSerializer(serializers.Serializer):
    text = serializers.CharField()


class RoomFindRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    staff_id = serializers.IntegerField()

class RoomFindResponseSerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
