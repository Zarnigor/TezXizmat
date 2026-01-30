from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.db import models

from .models import Staff
from .authentication import StaffJWTAuthentication
from .permissions import IsStaff
from .serializers import (
    StaffRegisterRequestSerializer,
    StaffProfileSerializer,
    StaffLoginRequestSerializer,
    StaffLoginResponseSerializer,
    StaffLogoutRequestSerializer,
    StaffProfileUpdateRequestSerializer,
    StaffImageUpdateRequestSerializer,
    StaffResetPasswordRequestSerializer,
    StaffPublicListSerializer,
    StaffPublicDetailSerializer,
    MessageSerializer, StaffTokenRefreshResponseSerializer, DeleteAccountSerializer,
)
from .authentication import StaffJWTAuthentication
from .tokens import StaffTokenObtainPairSerializer
from django.db.models import Avg, Count, Q
from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from .models import Staff

class StaffRegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_staff"],
        request=StaffRegisterRequestSerializer,
        responses={201: StaffProfileSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Staff register. Email OTP VERIFY oldindan verified bo‘lishi shart."
    )
    def post(self, request):
        ser = StaffRegisterRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(StaffProfileSerializer(user).data, status=status.HTTP_201_CREATED)


class StaffLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_staff"],
        request=StaffLoginRequestSerializer,
        responses={200: StaffLoginResponseSerializer, 400: OpenApiResponse(description="Invalid credentials")},
        description="Staff login. Access & refresh token qaytaradi."
    )
    def post(self, request):
        ser = StaffLoginRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        email = ser.validated_data["email"]
        password = ser.validated_data["password"]

        user = Staff.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "Email yoki parol xato."}, status=400)

        if not user.is_active:
            return Response({"detail": "Account aktiv emas."}, status=400)

        if not user.is_email_verified:
            return Response({"detail": "Email tasdiqlanmagan."}, status=400)

        if not user.check_password(password):
            return Response({"detail": "Email yoki parol xato."}, status=400)

        token = StaffTokenObtainPairSerializer.get_token(user)
        data = {
            "access": str(token.access_token),
            "refresh": str(token),
            "token_type": "Bearer",
            "user": StaffProfileSerializer(user).data,
        }
        return Response(data, status=200)


class StaffLogoutView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaff]

    @extend_schema(
        tags=["auth_staff"],
        request=StaffLogoutRequestSerializer,
        responses={200: MessageSerializer},
        description="Staff logout. Refresh token blacklist qilinadi."
    )
    def post(self, request):
        ser = StaffLogoutRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"message": "Logged out"}, status=200)


class StaffTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_staff"],
        request=TokenRefreshSerializer,
        responses={200: StaffTokenRefreshResponseSerializer},
        description="Staff token refresh (refresh -> new access)."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class StaffProfileView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaff]

    @extend_schema(
        tags=["auth_staff"],
        responses={200: StaffProfileSerializer},
        description="Staff o‘z profilini ko‘radi."
    )
    def get(self, request):
        return Response(StaffProfileSerializer(request.user).data, status=200)

    @extend_schema(
        tags=["auth_staff"],
        request=StaffProfileUpdateRequestSerializer,
        responses={200: StaffProfileSerializer},
        description="Staff profilini to‘liq update qiladi."
    )
    def put(self, request):
        ser = StaffProfileUpdateRequestSerializer(request.user, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(StaffProfileSerializer(request.user).data, status=200)

    @extend_schema(
        tags=["auth_staff"],
        request=StaffProfileUpdateRequestSerializer,
        responses={200: StaffProfileSerializer},
        description="Staff profilini qisman update qiladi."
    )
    def patch(self, request):
        ser = StaffProfileUpdateRequestSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(StaffProfileSerializer(request.user).data, status=200)


class StaffProfileImageView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaff]

    @extend_schema(
        tags=["auth_staff"],
        request=StaffImageUpdateRequestSerializer,
        responses={200: StaffPublicDetailSerializer},
        description="Staff rasmni alohida update qiladi (multipart/form-data)."
    )
    def put(self, request):
        ser = StaffImageUpdateRequestSerializer(request.user, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(StaffPublicDetailSerializer(request.user).data, status=200)


class StaffResetPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_staff"],
        request=StaffResetPasswordRequestSerializer,
        responses={200: MessageSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Staff reset password. RESET OTP verified bo‘lishi shart."
    )
    def post(self, request):
        ser = StaffResetPasswordRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        email = ser.validated_data["email"]
        password = ser.validated_data["password"]

        user = Staff.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "Staff topilmadi."}, status=400)

        if not user.is_email_verified:
            return Response({"detail": "Email tasdiqlanmagan."}, status=400)

        user.set_password(password)
        user.save(update_fields=["password", "updated_at"])
        return Response({"message": "Password updated successfully"}, status=200)


class StaffPublicListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = StaffPublicListSerializer
    queryset = Staff.objects.filter(is_active=True, is_email_verified=True)

    @extend_schema(
        tags=["staff"],
        parameters=[
            OpenApiParameter(name="search", required=False, type=str, description="Search: first_name, last_name, profession"),
        ],
        responses={200: StaffPublicListSerializer(many=True)},
        description="Public staff list (qidiruv bilan)."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        s = (self.request.query_params.get("search") or "").strip()
        if s:
            qs = qs.filter(
                models.Q(first_name__icontains=s) |
                models.Q(last_name__icontains=s) |
                models.Q(profession__icontains=s)
            )
        return qs


class StaffPublicDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = StaffPublicDetailSerializer

    def get_queryset(self):
        qs = Staff.objects.filter(is_active=True, is_email_verified=True)

        # reviews app bo‘lmasa ham yiqilmasin
        try:
            # related_name="reviews"
            qs = qs.annotate(
                avg_star=Avg("reviews__stars"),
                ratings_count=Count("reviews"),
                text_reviews_count=Count("reviews", filter=Q(reviews__text__gt="")),
            )
        except Exception:
            qs = qs.annotate(
                avg_star=Avg("id"),          # dummy (hech kim foydalanmaydi)
                ratings_count=Count("id"),    # dummy
                text_reviews_count=Count("id")# dummy
            )

        return qs

    @extend_schema(
        tags=["staff"],
        responses={200: StaffPublicDetailSerializer},
        description="Public staff detail + review statistics (avg_star, ratings_count, text_reviews_count)."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StaffDeleteAccountView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaff]

    @extend_schema(
        tags=["auth_staff"],
        request=DeleteAccountSerializer,
        responses={
            200: OpenApiResponse(description="Staff account deleted"),
            400: OpenApiResponse(description="Password invalid"),
            401: OpenApiResponse(description="Unauthorized"),
        },
        description="Staff o'z accountini parol bilan tasdiqlab o'chiradi."
    )
    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        staff = request.user
        staff.delete()
        return Response({"message": "Account o'chirildi"}, status=status.HTTP_200_OK)
