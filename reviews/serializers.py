from rest_framework import serializers
from .models import Review

class ReviewCreateRequestSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    stars = serializers.IntegerField(min_value=1, max_value=5)
    text = serializers.CharField(required=False, allow_blank=True)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = (
            "id",
            "order_id",
            "staff_id",
            "customer_id",
            "stars",
            "text",
            "created_at",
        )

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
