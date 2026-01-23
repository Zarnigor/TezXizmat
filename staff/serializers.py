import re
from rest_framework import serializers
from .models import Staff
from .utils import create_staff_tokens


def validate_password_rule(password: str) -> str:
    if len(password) < 8:
        raise serializers.ValidationError("Parol kamida 8 ta belgidan iborat bo‘lsin.")
    if not re.search(r"[A-Za-z]", password):
        raise serializers.ValidationError("Parolda kamida 1 ta harf bo‘lishi kerak.")
    if not re.search(r"\d", password):
        raise serializers.ValidationError("Parolda kamida 1 ta raqam bo‘lishi kerak.")
    return password


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LoginResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    refresh = serializers.CharField()
    access = serializers.CharField()

class StaffRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)

    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_password(self, value):
        return validate_password_rule(value)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Parollar mos emas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        staff = Staff.objects.create_user(password=password, **validated_data)
        return staff


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        # image YO'Q
        fields = [
            "id", "email", "first_name", "last_name",
            "profession",  "description", "skills",
            "price", "free_time",
            "is_active",
        ]
        read_only_fields = ["id", "email", "is_active"]


class StaffImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ["image"]


class StaffResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_password(self, value):
        return validate_password_rule(value)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Parollar mos emas."})
        return attrs

# Public list item
class StaffListSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    ratings_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Staff
        fields = ["id", "first_name", "last_name", "image", "profession", "price", "free_time", "avg_rating", "ratings_count"]


class MessageSerializer:
    pass


class StaffDetailSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    ratings_count = serializers.IntegerField(read_only=True)
    reviews_text_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Staff
        fields = [
            "id", "first_name", "last_name", "email", "image",
            "profession", "comments", "description", "skills", "price", "free_time",
            "avg_rating", "ratings_count", "reviews_text_count",
        ]

