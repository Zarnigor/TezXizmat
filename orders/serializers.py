from rest_framework import serializers
from .models import Order

class OrderCreateRequestSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    address = serializers.CharField(max_length=255)
    problem_text = serializers.CharField()

class OrderCancelRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)

class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id", "status", "address", "problem_text",
            "customer_id", "staff_id",
            "created_at", "accepted_at", "started_at",
            "completed_by_staff_at", "completed_by_customer_at",
            "canceled_at", "canceled_by",
        )

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id",
            "customer_id", "staff_id",
            "address", "problem_text",
            "status",
            "created_at", "accepted_at", "started_at",
            "completed_by_staff_at", "completed_by_customer_at",
            "canceled_at", "canceled_by", "cancel_reason",
        )

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
