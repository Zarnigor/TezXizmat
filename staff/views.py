from django.db.models import Avg, Count, Q
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema

from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from email_otp.models import EmailOTP
from .authentication import StaffJWTAuthentication
from .permissions import IsStaffUser
from .serializers import *
from .tokens import create_staff_tokens
from customer.serializers import LoginResponseSerializer, LoginSerializer


class StaffRegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth_staff"],
        request=StaffRegisterSerializer,
        responses={201: StaffProfileSerializer},
        description=""
    )
    def post(self, request):
        serializer = StaffRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
        return Response(StaffProfileSerializer(staff).data, status=status.HTTP_201_CREATED)


class StaffProfileView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsStaffUser]

    @extend_schema(tags=["auth_staff"], responses={200: StaffProfileSerializer})
    def get(self, request):
        return Response(StaffProfileSerializer(request.user).data)

    @extend_schema(
        tags=["auth_staff"],
        request=StaffProfileSerializer,
        responses={200: StaffProfileSerializer},
        description="Profile update (image qabul qilinmaydi). Image uchun alohida endpoint bor."
    )
    def patch(self, request):
        if "image" in request.data:
            return Response({"error": "Image update alohida endpoint orqali qilinadi."}, status=400)

        serializer = StaffProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)


class StaffProfileImageView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsStaffUser]

    @extend_schema(
        tags=["auth_staff"],
        request=StaffImageSerializer,
        responses={200: StaffImageSerializer},
        description="Staff rasmni alohida update qiladi (multipart/form-data, image field)."
    )
    def put(self, request):
        serializer = StaffImageSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)


class StaffLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth_staff"],
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            400: OpenApiResponse(description="Invalid credentials / inactive"),
        },
        description="Staff login. is_active=True bo‘lishi shart (OTP verify qilingan)."
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            staff = Staff.objects.get(email=email)
        except Staff.DoesNotExist:
            return Response({"detail": "Email yoki parol xato."}, status=400)

        if not staff.check_password(password):
            return Response({"detail": "Email yoki parol xato."}, status=400)

        if not staff.is_active:
            return Response({"detail": "Email tasdiqlanmagan (OTP verify qiling)."}, status=400)

        tokens = create_staff_tokens(staff)
        return Response(tokens, status=200)


class StaffLogoutView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsStaffUser]

    @extend_schema(
        tags=["auth_staff"],
        request=None,
        responses={200: OpenApiResponse(description="Logged out")},
        description="Refresh tokenni blacklist qiladi. Body: {refresh: <token>}"
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "refresh token required"}, status=400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=400)

        return Response({"detail": "Logged out"}, status=200)


# -------- PUBLIC STAFF CATALOG --------

class StaffListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = StaffListSerializer

    @extend_schema(
        tags=["staff"],
        parameters=[
            OpenApiParameter(name="search", type=str, required=False, description="first_name, last_name, profession bo‘yicha qidiruv"),
        ],
        responses={200: StaffListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = Staff.objects.filter(is_active=True)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(profession__icontains=search)
            )

        # Review modeli bor bo'lsa annotate ishlaydi:
        # from reviews.models import Review
        qs = qs.annotate(
            avg_rating=Avg("review__stars"),
            ratings_count=Count("review", distinct=True),
        )
        return qs


class StaffDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = StaffDetailSerializer
    queryset = Staff.objects.filter(is_active=True)

    @extend_schema(tags=["staff"], responses={200: StaffDetailSerializer})
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(
            avg_rating=Avg("review__stars"),
            ratings_count=Count("review", distinct=True),
            reviews_text_count=Count("review", filter=Q(review__text__isnull=False) & ~Q(review__text=""), distinct=True),
        )


class StaffResetPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = StaffResetPasswordSerializer

    @extend_schema(
        tags=["auth_staff"],
        request=StaffResetPasswordSerializer,
        responses={200: MessageSerializer},
        description=(
            "OTP verified bo‘lgandan keyin parolni yangilaydi. "
            "Oldin /api/auth/staff/send-email/ (PURPOSE_RESET), keyin /verify-email/ qilish shart."
        )
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
            staff = Staff.objects.get(email=email)
        except Staff.DoesNotExist:
            return Response(
                {"error": "Staff topilmadi"},
                status=404
            )

        staff.set_password(serializer.validated_data["password"])
        staff.save(update_fields=["password"])

        otp.state = EmailOTP.STATE_USED
        otp.save(update_fields=["state"])

        return Response(
            {"message": "Parol muvaffaqiyatli yangilandi"},
            status=200
        )
