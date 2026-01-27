from rest_framework import serializers
from .models import Order
from customer.models import Customer
from staff.models import Staff


# --- Nested serializers (response uchun) ---

class CustomerInfoSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ("id", "first_name", "last_name", "email", "full_name")

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class StaffInfoSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "profession",
            "description",
            "skills",
            "price",
            "free_time",
            "image",
            "is_active",
            "full_name",
        )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class OrderActionSerializer(serializers.Serializer):
    """
    Accept / Cancel / Complete uchun
    request body BO‘SH bo‘ladi
    """
    pass


class OrderCreateSerializer(serializers.ModelSerializer):
    staff_id = serializers.IntegerField(write_only=True)

    # frontdan keladi, lekin DBga yozilmaydi
    name = serializers.CharField(write_only=True, required=False)
    surname = serializers.CharField(write_only=True, required=False)

    # response uchun: staff object
    staff = StaffInfoSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "staff_id",   # request
            "staff",      # response
            "name",
            "surname",
            "description",
            "address",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")

    def validate_staff_id(self, value):
        if not Staff.objects.filter(id=value).exists():
            raise serializers.ValidationError("Staff topilmadi")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        customer = request.user

        staff_id = validated_data.pop("staff_id")

        # kelgan, lekin ishlatilmaydigan fieldlar
        validated_data.pop("name", None)
        validated_data.pop("surname", None)

        # DB uchun title default: "hi"
        validated_data.setdefault("title", "hi")

        return Order.objects.create(
            customer=customer,
            staff_id=staff_id,
            **validated_data
        )


class OrderListSerializer(serializers.ModelSerializer):
    staff = StaffInfoSerializer(read_only=True)
    customer = CustomerInfoSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "staff",
            "address",
            "description",
            "status",
            "created_at",
        )


class OrderDetailSerializer(serializers.ModelSerializer):
    staff = StaffInfoSerializer(read_only=True)
    customer = CustomerInfoSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "staff",
            "description",
            "address",
            "status",
            "accepted_at",
            "completed_at",
            "canceled_at",
            "created_at",
            "updated_at",
        )
