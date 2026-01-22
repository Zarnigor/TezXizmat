from rest_framework import serializers
from .models import Review

class ReviewCreateSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Review
        fields = ["id", "staff", "rating", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_comment(self, value):
        if value is None:
            return None
        value = value.strip()
        return value if value else None


class ReviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "staff", "rating", "comment", "created_at"]


class ReviewDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "customer", "staff", "rating", "comment", "created_at", "updated_at"]
