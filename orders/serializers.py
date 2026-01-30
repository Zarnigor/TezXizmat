from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Order


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

    profession = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    skills_text = serializers.CharField(allow_blank=True)
    price_text = serializers.CharField(allow_blank=True)
    free_time_text = serializers.CharField(allow_blank=True)


class OrderCreateRequestSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    address = serializers.CharField(max_length=255)
    problem_text = serializers.CharField()


class OrderCancelRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)


class OrderDetailSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "address",
            "problem_text",

            "customer_id",
            "staff_id",
            "customer",
            "staff",

            "created_at",
            "accepted_at",
            "started_at",
            "completed_by_staff_at",
            "completed_by_customer_at",
            "canceled_at",
            "canceled_by",
            "cancel_reason",
        )

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


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "address",
            "problem_text",
            "customer_id",
            "staff_id",
            "created_at",
        )


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
