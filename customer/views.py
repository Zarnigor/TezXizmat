from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import GenericAPIView
from .models import Customer
from .serializers import (
    RegisterSerializer,
    ResetPasswordSerializer,
    ProfileSerializer,
    EmptySerializer,
    MessageSerializer,
    LoginSerializer, LoginResponseSerializer,
)
from email_otp.models import EmailOTP



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


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: LoginResponseSerializer}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


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

