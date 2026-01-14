from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Customer
from .models import EmailOTP
from .serializers import (
    SendEmailSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    ProfileSerializer, VerifyEmailSerializer, ResendEmailSerializer, EmptySerializer, MessageSerializer, LoginSerializer
)


@extend_schema(
    request=SendEmailSerializer,
    responses={200: OpenApiResponse(description="OTP emailga yuborildi")}
)
class SendEmailOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()

        return Response({
            "detail": "Kod emailga yuborildi",
            "email": otp.email,
            "expires_at": otp.expires_at
        })


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
        serializer.save()

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


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        # faqat serializable tiplar yuborish kerak
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "email": user.email,   # username o‘rniga email
                "first_name": user.first_name,
                "last_name": user.last_name
            },
            status=status.HTTP_200_OK
        )

from rest_framework.generics import GenericAPIView

class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    @extend_schema(
        responses={200: MessageSerializer}
    )
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

    @extend_schema(
        request=ProfileSerializer,
        responses={200: OpenApiResponse(description="Profile updated successfully")}
    )
    def put(self, request):
        serializer = ProfileSerializer(data=request.data, instance=request.user, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

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


class ResetPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    @extend_schema(
        request=ResetPasswordSerializer,
        responses={200: MessageSerializer}
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        otp = EmailOTP.objects.filter(
            email=email,
            purpose=EmailOTP.PURPOSE_RESET,
            state=EmailOTP.STATE_VERIFIED
        ).last()

        if not otp:
            return Response(
                {"error": "Avval emailga yuborilgan kodni tasdiqlang"},
                status=400
            )

        try:
            user = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Foydalanuvchi topilmadi"},
                status=404
            )

        user.set_password(serializer.validated_data["password"])
        user.save(update_fields=["password"])

        otp.state = EmailOTP.STATE_USED
        otp.save(update_fields=["state"])

        return Response(
            {"message": "Parol muvaffaqiyatli yangilandi"},
            status=200
        )



@extend_schema(
    request=ResendEmailSerializer,
    responses={200: OpenApiResponse(description="OTP qayta yuborildi")}
)
class ResendEmailOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()

        return Response({
            "detail": "Yangi kod yuborildi",
            "expires_at": otp.expires_at
        })
