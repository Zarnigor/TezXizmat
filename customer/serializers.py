# customer/serializers.py
from rest_framework import serializers
from .models import Customer

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

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
    password = serializers.CharField()

class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('email', 'first_name', 'last_name', 'image')
        read_only_fields = ('email',)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, write_only=True)

    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {"password": "Parollar mos emas"}
            )

        # 8 ta belgi, harf + son
        validate_password(password)

        return attrs
