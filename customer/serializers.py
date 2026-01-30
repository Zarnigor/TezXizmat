from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Customer
from .validators import validate_password_policy


def _norm_email(email: str) -> str:
    return (email or "").strip().lower()


def _email_verified_by_otp(email: str, purpose: str) -> bool:
    """
    email_otp appdan tekshiradi:
      is_email_verified(email, purpose, actor)
    actor = CUSTOMER
    """
    try:
        from email_otp.services import is_email_verified  # type: ignore
        from email_otp.models import EmailOTP  # type: ignore
    except Exception:
        raise serializers.ValidationError(
            {"detail": "email_otp app/service topilmadi. (email_otp.services.is_email_verified)"}
        )

    return is_email_verified(email=_norm_email(email), purpose=purpose, actor=EmailOTP.ACTOR_CUSTOMER)


def _email_exists_in_staff(email: str) -> bool:
    try:
        from staff.models import Staff  # type: ignore
        return Staff.objects.filter(email=_norm_email(email)).exists()
    except Exception:
        # staff app hali bo‘lmasligi mumkin
        return False


class CustomerRegisterRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=80)
    last_name = serializers.CharField(max_length=80)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return _norm_email(value)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Parollar mos emas."})

        validate_password_policy(attrs["password"])

        email = attrs["email"]

        # Email registerdan OLDIN OTP VERIFY bo‘lishi shart
        if not _email_verified_by_otp(email=email, purpose="VERIFY"):
            raise serializers.ValidationError({"email": "Email avval OTP orqali tasdiqlanishi kerak (VERIFY)."})

        # Global unique (Customer + Staff)
        if Customer.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Bu email allaqachon customer sifatida ro‘yxatdan o‘tgan."})
        if _email_exists_in_staff(email):
            raise serializers.ValidationError({"email": "Bu email staff akkauntida band."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = Customer.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"].strip(),
            last_name=validated_data["last_name"].strip(),
            is_email_verified=True,
        )
        return user


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("id", "first_name", "last_name", "email", "image", "is_email_verified", "created_at")


class CustomerMiniSerializer(serializers.ModelSerializer):
    """customer/<id> uchun (faqat ism/familiya/image)"""
    class Meta:
        model = Customer
        fields = ("id", "first_name", "last_name", "image")


class CustomerLoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return _norm_email(value)


class CustomerLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    token_type = serializers.CharField()
    user = CustomerProfileSerializer()


class CustomerLogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        token = RefreshToken(self.validated_data["refresh"])
        token.blacklist()


class CustomerProfileUpdateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("first_name", "last_name")

    def validate_first_name(self, v): return v.strip()
    def validate_last_name(self, v): return v.strip()


class CustomerImageUpdateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("image",)


class CustomerResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return _norm_email(value)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Parollar mos emas."})
        validate_password_policy(attrs["password"])

        email = attrs["email"]

        # RESET OTP verified bo‘lishi shart
        if not _email_verified_by_otp(email=email, purpose="RESET"):
            raise serializers.ValidationError({"detail": "Avval RESET OTP tasdiqlanishi kerak."})

        return attrs


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class CustomerTokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
