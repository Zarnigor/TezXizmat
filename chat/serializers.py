from rest_framework import serializers
from .models import ChatRoom, ChatMessage


# =================================================
# Public Out (customer / staff)
# =================================================
class CustomerPublicOutSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    image = serializers.CharField(allow_null=True)


class StaffPublicOutSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    image = serializers.CharField(allow_null=True)

    profession = serializers.CharField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    skills_text = serializers.CharField(allow_null=True)
    price_text = serializers.CharField(allow_null=True)
    free_time_text = serializers.CharField(allow_null=True)


# =================================================
# Messages
# =================================================
class ChatMessageOutSerializer(serializers.ModelSerializer):
    # IMPORTANT: source="sender_type" qo'ymaymiz!
    sender_type = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ("id", "text", "sender_type", "created_at")

    def get_sender_type(self, obj):
        # ChatMessage modelida @property sender_type bo'lsa shu ishlaydi
        return obj.sender_type


class ChatMessageSendInSerializer(serializers.Serializer):
    text = serializers.CharField(allow_blank=False, trim_whitespace=True)


# =================================================
# Room create / find input
# =================================================
class ChatRoomCreateInSerializer(serializers.Serializer):
    """
    Customer token bo'lsa: staff_id yuboradi
    Staff token bo'lsa: customer_id yuboradi
    order_id ixtiyoriy (nullable)
    """
    staff_id = serializers.IntegerField(required=False)
    customer_id = serializers.IntegerField(required=False)
    order_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        staff_id = attrs.get("staff_id")
        customer_id = attrs.get("customer_id")

        # Ikkalasini birga yubormaslik
        if staff_id and customer_id:
            raise serializers.ValidationError("Send only one of staff_id or customer_id.")

        # Hech narsa yubormaslik ham mumkin emas
        if not staff_id and not customer_id:
            raise serializers.ValidationError("Provide staff_id or customer_id.")

        return attrs


# =================================================
# Room Out (list / single)
# =================================================
class ChatRoomOutSerializer(serializers.ModelSerializer):
    # IMPORTANT: source="order_id" qo'ymaymiz!
    order_id = serializers.IntegerField(read_only=True)

    customer = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()

    last_message = serializers.SerializerMethodField()
    unreaded_message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = (
            "id",
            "order_id",
            "created_at",
            "customer",
            "staff",
            "last_message",
            "unreaded_message_count",
        )

    def get_customer(self, obj):
        c = obj.customer
        return {
            "id": c.id,
            "first_name": getattr(c, "first_name", ""),
            "last_name": getattr(c, "last_name", ""),
            "image": c.image.url if getattr(c, "image", None) else None,
        }

    def get_staff(self, obj):
        s = obj.staff
        return {
            "id": s.id,
            "first_name": getattr(s, "first_name", ""),
            "last_name": getattr(s, "last_name", ""),
            "image": s.image.url if getattr(s, "image", None) else None,
            "profession": getattr(s, "profession", None),
            "description": getattr(s, "description", None),
            "skills_text": getattr(s, "skills_text", None),
            "price_text": getattr(s, "price_text", None),
            "free_time_text": getattr(s, "free_time_text", None),
        }

    def get_last_message(self, obj):
        """
        View ichida obj._last_message_cache set qilinsa N+1 kamayadi.
        Aks holda fallback qilib DBdan oxirgisini oladi.
        """
        m = getattr(obj, "_last_message_cache", None)
        if m is None:
            m = obj.messages.order_by("-created_at").first()
        return ChatMessageOutSerializer(m).data if m else None

    def get_unreaded_message_count(self, obj):
        """
        Unread hisoblash:
          - Customer uchun: staff yozgan va customer o'qimaganlari
          - Staff uchun: customer yozgan va staff o'qimaganlari

        Modelda quyidagilar bo'lishi kerak:
          - customer_last_read_at
          - staff_last_read_at
        """
        request = self.context.get("request")
        if request is None:
            return 0

        user = request.user
        user_type = user.__class__.__name__

        if user_type == "Customer":
            last_read_at = getattr(obj, "customer_last_read_at", None)
            qs = obj.messages.exclude(sender_customer_id=obj.customer_id)
        elif user_type == "Staff":
            last_read_at = getattr(obj, "staff_last_read_at", None)
            qs = obj.messages.exclude(sender_staff_id=obj.staff_id)
        else:
            return 0

        if last_read_at:
            qs = qs.filter(created_at__gt=last_read_at)

        return qs.count()
