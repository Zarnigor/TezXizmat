from rest_framework import serializers
from .models import EmailOTP


class SendOTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=EmailOTP.PURPOSE_CHOICES)


class VerifyOTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=10)
    purpose = serializers.ChoiceField(choices=EmailOTP.PURPOSE_CHOICES)


class OTPMessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    email = serializers.EmailField()
    purpose = serializers.CharField()
    expires_in = serializers.IntegerField(required=False)
