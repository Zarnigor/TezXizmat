from rest_framework import serializers
from .models import Review

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class ReviewCreateRequestSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    stars = serializers.IntegerField(min_value=1, max_value=5)
    text = serializers.CharField(required=False, allow_blank=True)


class ReviewSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            "id",
            "order_id",
            "stars",
            "text",
            "created_at",
            "customer_id",
            "staff_id",
            "customer",   # ✅ customer info (id, name, image)
            "staff",      # ✅ staff info (email yo‘q)
        )

    def get_customer(self, obj):
        c = obj.customer
        return {
            "id": c.id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "image": c.image.url if getattr(c, "image", None) else None,
        }

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
