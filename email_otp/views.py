from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import EmailOTP
from .serializers import (
    SendOTPRequestSerializer,
    VerifyOTPRequestSerializer,
    OTPMessageResponseSerializer,
)
from .services import send_otp, verify_otp, OTP_EXPIRE_SECONDS


# ---------- CUSTOMER ----------
class CustomerSendEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_customer"],
        request=SendOTPRequestSerializer,
        responses={200: OTPMessageResponseSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Customer uchun OTP yuboradi (VERIFY yoki RESET)."
    )
    def post(self, request):
        ser = SendOTPRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        send_otp(
            email=ser.validated_data["email"],
            purpose=ser.validated_data["purpose"],
            actor=EmailOTP.ACTOR_CUSTOMER,
        )
        return Response(
            {
                "message": "OTP sent",
                "email": ser.validated_data["email"].strip().lower(),
                "purpose": ser.validated_data["purpose"],
                "expires_in": OTP_EXPIRE_SECONDS,
            },
            status=200,
        )


class CustomerResendEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_customer"],
        request=SendOTPRequestSerializer,
        responses={200: OTPMessageResponseSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Customer uchun OTP qayta yuboradi (VERIFY yoki RESET)."
    )
    def post(self, request):
        ser = SendOTPRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        send_otp(
            email=ser.validated_data["email"],
            purpose=ser.validated_data["purpose"],
            actor=EmailOTP.ACTOR_CUSTOMER,
        )
        return Response(
            {
                "message": "OTP resent",
                "email": ser.validated_data["email"].strip().lower(),
                "purpose": ser.validated_data["purpose"],
                "expires_in": OTP_EXPIRE_SECONDS,
            },
            status=200,
        )


class CustomerVerifyEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_customer"],
        request=VerifyOTPRequestSerializer,
        responses={200: OTPMessageResponseSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Customer OTP tasdiqlaydi (VERIFY yoki RESET)."
    )
    def post(self, request):
        ser = VerifyOTPRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        verify_otp(
            email=ser.validated_data["email"],
            code=ser.validated_data["code"],
            purpose=ser.validated_data["purpose"],
            actor=EmailOTP.ACTOR_CUSTOMER,
        )
        return Response(
            {
                "message": "OTP verified",
                "email": ser.validated_data["email"].strip().lower(),
                "purpose": ser.validated_data["purpose"],
            },
            status=200,
        )


# ---------- STAFF ----------
class StaffSendEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_staff"],
        request=SendOTPRequestSerializer,
        responses={200: OTPMessageResponseSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Staff uchun OTP yuboradi (VERIFY yoki RESET)."
    )
    def post(self, request):
        ser = SendOTPRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        send_otp(
            email=ser.validated_data["email"],
            purpose=ser.validated_data["purpose"],
            actor=EmailOTP.ACTOR_STAFF,
        )
        return Response(
            {
                "message": "OTP sent",
                "email": ser.validated_data["email"].strip().lower(),
                "purpose": ser.validated_data["purpose"],
                "expires_in": OTP_EXPIRE_SECONDS,
            },
            status=200,
        )


class StaffResendEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_staff"],
        request=SendOTPRequestSerializer,
        responses={200: OTPMessageResponseSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Staff uchun OTP qayta yuboradi (VERIFY yoki RESET)."
    )
    def post(self, request):
        ser = SendOTPRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        send_otp(
            email=ser.validated_data["email"],
            purpose=ser.validated_data["purpose"],
            actor=EmailOTP.ACTOR_STAFF,
        )
        return Response(
            {
                "message": "OTP resent",
                "email": ser.validated_data["email"].strip().lower(),
                "purpose": ser.validated_data["purpose"],
                "expires_in": OTP_EXPIRE_SECONDS,
            },
            status=200,
        )


class StaffVerifyEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_staff"],
        request=VerifyOTPRequestSerializer,
        responses={200: OTPMessageResponseSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Staff OTP tasdiqlaydi (VERIFY yoki RESET)."
    )
    def post(self, request):
        ser = VerifyOTPRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        verify_otp(
            email=ser.validated_data["email"],
            code=ser.validated_data["code"],
            purpose=ser.validated_data["purpose"],
            actor=EmailOTP.ACTOR_STAFF,
        )
        return Response(
            {
                "message": "OTP verified",
                "email": ser.validated_data["email"].strip().lower(),
                "purpose": ser.validated_data["purpose"],
            },
            status=200,
        )
