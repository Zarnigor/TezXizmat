from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    SendEmailSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    ProfileSerializer, VerifyEmailSerializer
)
from .utils import generate_otp, send_email

@extend_schema(
    request=SendEmailSerializer,
    responses={200: OpenApiResponse(description="OTP emailga yuborildi")}
)
class SendEmailOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        purpose = serializer.validated_data["purpose"]

        EmailOTP.objects.filter(email=email, purpose=purpose).delete()

        otp = EmailOTP.objects.create(
            email=email,
            code=generate_otp(),
            purpose=purpose,
            state=EmailOTP.STATE_SEND
        )

        send_email(email, otp.code)

        return Response({"detail": "Kod emailga yuborildi"})

@extend_schema(
    request=VerifyEmailSerializer,
    responses={
        200: OpenApiResponse(description="Email tasdiqlandi"),
        400: OpenApiResponse(description="Xatolik")
    }
)
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        purpose = serializer.validated_data["purpose"]

        otp = EmailOTP.objects.filter(
            email=email,
            code=code,
            purpose=purpose,
            state=EmailOTP.STATE_SEND
        ).last()

        if not otp or otp.is_expired():
            return Response(
                {"error": "Kod noto‘g‘ri yoki eskirgan"},
                status=400
            )

        otp.state = EmailOTP.STATE_VERIFIED
        otp.save()

        return Response({"detail": "Kod tasdiqlandi"})


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
            state="VERIFIED"
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

        Customer.objects.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_active=True
        )

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

    @extend_schema(
        responses={200: ProfileSerializer}
    )
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProfileSerializer,
        responses={200: ProfileSerializer}
    )
    def put(self, request):
        serializer = ProfileSerializer(
            request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        request=ProfileSerializer,
        responses={200: ProfileSerializer}
    )
    def patch(self, request):
        serializer = ProfileSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

from .serializers import ResetPasswordSerializer
from .models import EmailOTP
from .models import Customer

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = EmailOTP.objects.filter(
            purpose=EmailOTP.PURPOSE_RESET,
            state=EmailOTP.STATE_VERIFIED
        ).last()

        if not otp:
            return Response(
                {"error": "Avval kodni tasdiqlang"},
                status=400
            )

        user = Customer.objects.get(email=otp.email)

        user.set_password(serializer.validated_data["password"])
        user.save()

        otp.state = EmailOTP.STATE_USED
        otp.save()

        return Response({"detail": "Parol muvaffaqiyatli yangilandi"})
