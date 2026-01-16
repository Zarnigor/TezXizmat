
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SendEmailSerializer, VerifyEmailSerializer, ResendEmailSerializer


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