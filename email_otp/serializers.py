from datetime import timedelta

from django.utils.timezone import now
from rest_framework import serializers

from .utils import send_email, generate_otp
from .models import EmailOTP


class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(
        choices=EmailOTP.PURPOSE_CHOICES,
        default=EmailOTP.PURPOSE_VERIFY
    )

    def create(self, validated_data):
        email = validated_data["email"]
        purpose = validated_data["purpose"]

        otp = EmailOTP.objects.create(
            email=email,
            purpose=purpose,
            code=generate_otp(),
            expires_at=now() + timedelta(seconds=60)
        )

        send_email(email, otp.code)

        return otp


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(
        choices=EmailOTP.PURPOSE_CHOICES,
        default=EmailOTP.PURPOSE_VERIFY
    )

    def validate(self, attrs):
        email = attrs["email"]
        code = attrs["code"]
        purpose = attrs["purpose"]

        otp = EmailOTP.objects.filter(
            email=email,
            code=code,
            purpose=purpose,
            state=EmailOTP.STATE_SEND
        ).last()

        if not otp:
            raise serializers.ValidationError("Kod noto‘g‘ri")

        if otp.is_expired():
            raise serializers.ValidationError("Kod muddati tugagan")

        attrs["otp"] = otp
        return attrs

    def save(self, **kwargs):
        otp = self.validated_data["otp"]
        otp.state = EmailOTP.STATE_VERIFIED
        otp.save(update_fields=["state"])
        return otp


class ResendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(
        choices=EmailOTP.PURPOSE_CHOICES,
        default=EmailOTP.PURPOSE_VERIFY
    )

    def validate(self, attrs):
        email = attrs["email"]
        purpose = attrs["purpose"]

        last_otp = EmailOTP.objects.filter(
            email=email,
            purpose=purpose
        ).order_by("-created_at").first()

        if last_otp and not last_otp.is_expired():
            remaining = int((last_otp.expires_at - now()).total_seconds())
            raise serializers.ValidationError(
                f"{remaining} sekunddan keyin qayta yuborish mumkin"
            )

        return attrs

    def create(self, validated_data):
        email = validated_data["email"]
        purpose = validated_data["purpose"]

        otp = EmailOTP.objects.create(
            email=email,
            purpose=purpose,
            code=generate_otp(),
            expires_at=now() + timedelta(seconds=60)
        )

        send_email(email, otp.code)

        return otp

