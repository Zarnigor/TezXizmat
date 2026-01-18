from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Customer
from .validators import validate_password


class EmptySerializer(serializers.Serializer):
    pass


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError("Passwords do not match")

        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")

        if password.isdigit() or password.isalpha():
            raise serializers.ValidationError("Password must contain letters and numbers")

        return data

    class Meta:
        model = Customer
        fields = ('email', 'password', 'password2', 'first_name', 'last_name')


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Email yoki password noto‘g‘ri")
        if not user.is_active:
            raise serializers.ValidationError("User aktiv emas")

        attrs["user"] = user
        return attrs


class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('email', 'first_name', 'last_name')
        read_only_fields = ('email',)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Parollar mos emas"}
            )

        validate_password(attrs["password"])
        return attrs

