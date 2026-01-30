from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Staff
from .validators import validate_password_policy


def _norm_email(email: str) -> str:
    return (email or "").strip().lower()


def _email_verified_by_otp(email: str, purpose: str) -> bool:
    try:
        from email_otp.services import is_email_verified  # type: ignore
        from email_otp.models import EmailOTP  # type: ignore
    except Exception:
        raise serializers.ValidationError(
            {"detail": "email_otp app/service topilmadi. (email_otp.services.is_email_verified)"}
        )

    return is_email_verified(email=_norm_email(email), purpose=purpose, actor=EmailOTP.ACTOR_STAFF)


def _email_exists_in_customer(email: str) -> bool:
    try:
        from customer.models import Customer  # type: ignore
        return Customer.objects.filter(email=_norm_email(email)).exists()
    except Exception:
        return False


class StaffRegisterRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=80)
    last_name = serializers.CharField(max_length=80)
    profession = serializers.CharField(max_length=120)

    description = serializers.CharField(required=False, allow_blank=True)
    skills_text = serializers.CharField(required=False, allow_blank=True)
    price_text = serializers.CharField(required=False, allow_blank=True)
    free_time_text = serializers.CharField(required=False, allow_blank=True)

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, v):
        return _norm_email(v)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Parollar mos emas."})

        validate_password_policy(attrs["password"])

        email = attrs["email"]

        # Email registerdan oldin OTP VERIFY bo‘lishi shart
        if not _email_verified_by_otp(email=email, purpose="VERIFY"):
            raise serializers.ValidationError({"email": "Email avval OTP orqali tasdiqlanishi kerak (VERIFY)."})

        # Global unique: Staff + Customer
        if Staff.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Bu email allaqachon staff sifatida ro‘yxatdan o‘tgan."})
        if _email_exists_in_customer(email):
            raise serializers.ValidationError({"email": "Bu email customer akkauntida band."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = Staff.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"].strip(),
            last_name=validated_data["last_name"].strip(),
            profession=validated_data["profession"].strip(),
            description=(validated_data.get("description") or "").strip(),
            skills_text=(validated_data.get("skills_text") or "").strip(),
            price_text=(validated_data.get("price_text") or "").strip(),
            free_time_text=(validated_data.get("free_time_text") or "").strip(),
            is_email_verified=True,
        )
        return user


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "image",
            "profession",
            "description",
            "skills_text",
            "price_text",
            "free_time_text",
            "is_email_verified",
            "created_at",
        )


class StaffPublicListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ("id", "first_name", "last_name", "image", "profession", "price_text")


from rest_framework import serializers
from .models import Staff

class StaffPublicDetailSerializer(serializers.ModelSerializer):
    avg_star = serializers.FloatField(read_only=True)
    ratings_count = serializers.IntegerField(read_only=True)
    text_reviews_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Staff
        fields = (
            "id",
            "first_name",
            "last_name",
            "image",
            "profession",
            "description",
            "skills_text",
            "price_text",
            "free_time_text",
            "avg_star",
            "ratings_count",
            "text_reviews_count",
        )



class StaffLoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, v):
        return _norm_email(v)


class StaffLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    token_type = serializers.CharField()
    user = StaffProfileSerializer()


class StaffLogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        RefreshToken(self.validated_data["refresh"]).blacklist()


class StaffProfileUpdateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ("first_name", "last_name", "profession", "description", "skills_text", "price_text", "free_time_text")

    def validate_first_name(self, v): return v.strip()
    def validate_last_name(self, v): return v.strip()
    def validate_profession(self, v): return v.strip()


class StaffImageUpdateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ("image",)


class StaffResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, v):
        return _norm_email(v)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Parollar mos emas."})
        validate_password_policy(attrs["password"])

        email = attrs["email"]
        if not _email_verified_by_otp(email=email, purpose="RESET"):
            raise serializers.ValidationError({"detail": "Avval RESET OTP tasdiqlanishi kerak."})

        return attrs


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class StaffTokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()