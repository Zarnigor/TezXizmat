from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.utils import timezone
from .models import User

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)   # parol xeshlansin
        user.is_active = True         # email tasdiqi bo‘lsa False ham bo‘lishi mumkin
        user.role = 'user'            # user rolini default belgilash
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'role', 'is_active']


class EmailOTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'User not found.'})

        if not user.login_otp or user.login_otp != otp:
            print(user.login_otp, otp)
            raise serializers.ValidationError({'otp': 'Invalid OTP code.'})

        if user.login_otp_expires and timezone.now() > user.login_otp_expires:
            raise serializers.ValidationError({'otp': 'OTP code expired.'})

        attrs['user'] = user
        return attrs

class LoginSendSmsSerializer(serializers.Serializer):
    email = serializers.EmailField()


class LoginVerifySmsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=8)


class UpdateSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['language', 'notifications_enabled']


class UpdateProfileSerializer(serializers.ModelSerializer):
    pin_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'pin_code']

    def validate_password(self, value):
        if value:
            validate_password(value)
        return value

    def update(self, instance, validated_data):
        pwd = validated_data.pop('pin_code', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if pwd:
            instance.set_password(pwd)
        instance.save()
        return instance