from datetime import timedelta

from django.utils.timezone import now
from rest_framework import serializers

from .models import Customer, EmailOTP
from .utils import send_email, generate_otp
from .validators import validate_password


class EmptySerializer(serializers.Serializer):
    pass

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


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
            state=EmailOTP.STATE_PENDING
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
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Parollar mos emas"}
            )

        validate_password(attrs["password"])
        return attrs


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
