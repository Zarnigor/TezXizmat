import random
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.permissions import AllowAny

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.views import TokenObtainPairView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse
)

from .models import Customer, EmailOTP
from .serializers import (
    SendEmailSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    ProfileSerializer
)
from .validators import validate_password

@extend_schema(
    request=SendEmailSerializer,
    responses={200: OpenApiResponse(description="OTP emailga yuborildi")}
)
class SendEmailOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = str(random.randint(100000, 999999))

        obj = EmailOTP.objects.filter(email=email)
        if obj:
            obj.code = code
        else:
            EmailOTP.objects.create(email=email, code=code)

        send_mail(
            subject="Tasdiqlash kodi",
            message=f"Sizning kodingiz: {code}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        return Response(
            {"detail": "Kod emailga yuborildi"},
            status=status.HTTP_200_OK
        )

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import EmailOTP
from django.utils.timezone import now
from datetime import timedelta

@extend_schema(
    parameters=[
        OpenApiParameter("email", str),
        OpenApiParameter("code", str),
    ],
    responses={200: OpenApiResponse(description="Email tasdiqlandi")}
)
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.GET.get("email", "").strip()
        code = request.GET.get("code", "").strip()

        otp = EmailOTP.objects.filter(email=email, code=code).last()

        if not otp:
            return Response({"error": "Kod noto‘g‘ri"}, status=400)

        if otp.is_expired():
            return Response({"error": "Kod muddati tugagan"}, status=400)

        otp.is_verified = True
        otp.save()  # 🔥 BU MUHIM
        return Response({"detail": "Email tasdiqlandi"}, status=200)


@extend_schema(
    request=RegisterSerializer,
    responses={201: OpenApiResponse(description="Account yaratildi")}
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        verified_otp = EmailOTP.objects.filter(
            email=data['email'],
            is_verified=True
        ).last()

        if not verified_otp:
            return Response(
                {"error": "Email tasdiqlanmagan"},
                status=status.HTTP_403_FORBIDDEN
            )

        if Customer.objects.filter(email=data['email']).exists():
            return Response(
                {"error": "Bu email allaqachon ro‘yxatdan o‘tgan"},
                status=400
            )

        user = Customer.objects.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_active=True
        )

        # OTP ni ishlatilgan deb belgilaymiz (ixtiyoriy)
        verified_otp.delete()

        return Response({"detail": "Ro‘yxatdan o‘tildi"}, status=201)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    """
    JWT login (email + password)
    """
    pass


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"detail": "Logout muvaffaqiyatli"}, status=200)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ProfileSerializer(
            request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        serializer = ProfileSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@extend_schema(
    request=ResetPasswordSerializer,
    responses={200: OpenApiResponse(description="Parol yangilandi")}
)
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        password = serializer.validated_data['password']

        otp = EmailOTP.objects.filter(email=email, code=code).last()
        if not otp or otp.is_expired():
            return Response({"error": "Kod noto‘g‘ri yoki eskirgan"}, status=400)

        user = Customer.objects.get(email=email)
        validate_password(password)
        user.set_password(password)
        user.save()

        return Response({"detail": "Parol muvaffaqiyatli yangilandi"})
