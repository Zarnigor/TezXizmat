from rest_framework import serializers
from .models import Order
from customer.models import Customer
from staff.models import Staff


class OrderActionSerializer(serializers.Serializer):
    """
    Accept / Cancel / Complete uchun
    request body BO‘SH bo‘ladi
    """
    pass

class OrderCreateSerializer(serializers.ModelSerializer):
    staff_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "staff_id",
            "title",
            "description",
            "address",
        )

    def validate_staff_id(self, value):
        if not Staff.objects.filter(id=value).exists():
            raise serializers.ValidationError("Staff topilmadi")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        customer = Customer.objects.get(user=request.user)
        staff_id = validated_data.pop("staff_id")

        return Order.objects.create(
            customer=customer,
            staff_id=staff_id,
            **validated_data
        )


class OrderListSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(
        source="staff.user.get_full_name",
        read_only=True
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "title",
            "address",
            "status",
            "staff_name",
            "created_at",
        )


class OrderDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.user.get_full_name",
        read_only=True
    )
    staff_name = serializers.CharField(
        source="staff.user.get_full_name",
        read_only=True
    )

    class Meta:
        model = Order
        fields = "__all__"
