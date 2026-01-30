from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView

from .authentication import CustomerJWTAuthentication
from .models import Customer
from .permissions import IsCustomer
from .serializers import (
    CustomerRegisterRequestSerializer,
    CustomerProfileSerializer,
    CustomerLoginRequestSerializer,
    CustomerLoginResponseSerializer,
    CustomerLogoutRequestSerializer,
    CustomerProfileUpdateRequestSerializer,
    CustomerImageUpdateRequestSerializer,
    CustomerResetPasswordRequestSerializer,
    CustomerMiniSerializer,
    MessageSerializer,
)
from .serializers import CustomerTokenRefreshResponseSerializer
from .tokens import CustomerTokenObtainPairSerializer


class CustomerRegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_customer"],
        request=CustomerRegisterRequestSerializer,
        responses={201: CustomerProfileSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Customer register. Email OTP VERIFY oldindan verified bo‘lishi shart."
    )
    def post(self, request):
        ser = CustomerRegisterRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(CustomerProfileSerializer(user).data, status=status.HTTP_201_CREATED)


class CustomerLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_customer"],
        request=CustomerLoginRequestSerializer,
        responses={200: CustomerLoginResponseSerializer, 400: OpenApiResponse(description="Invalid credentials")},
        description="Customer login. Access & refresh token qaytaradi."
    )
    def post(self, request):
        ser = CustomerLoginRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        email = ser.validated_data["email"]
        password = ser.validated_data["password"]

        try:
            user = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return Response({"detail": "Email yoki parol xato."}, status=400)

        if not user.is_active:
            return Response({"detail": "Account aktiv emas."}, status=400)

        if not user.is_email_verified:
            return Response({"detail": "Email tasdiqlanmagan."}, status=400)

        if not user.check_password(password):
            return Response({"detail": "Email yoki parol xato."}, status=400)

        token = CustomerTokenObtainPairSerializer.get_token(user)
        data = {
            "access": str(token.access_token),
            "refresh": str(token),
            "token_type": "Bearer",
            "user": CustomerProfileSerializer(user).data
        }
        return Response(data, status=200)


class CustomerLogoutView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        tags=["auth_customer"],
        request=CustomerLogoutRequestSerializer,
        responses={200: MessageSerializer},
        description="Customer logout. Refresh token blacklist qilinadi."
    )
    def post(self, request):
        ser = CustomerLogoutRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"message": "Logged out"}, status=200)


class CustomerTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_customer"],
        request=TokenRefreshSerializer,
        responses={200: CustomerTokenRefreshResponseSerializer},
        description="Customer token refresh (refresh -> new access)."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)



class CustomerProfileView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        tags=["auth_customer"],
        responses={200: CustomerProfileSerializer},
        description="Customer o‘z profilini ko‘radi."
    )
    def get(self, request):
        return Response(CustomerProfileSerializer(request.user).data, status=200)

    @extend_schema(
        tags=["auth_customer"],
        request=CustomerProfileUpdateRequestSerializer,
        responses={200: CustomerProfileSerializer},
        description="Customer profilini to‘liq update qiladi."
    )
    def put(self, request):
        ser = CustomerProfileUpdateRequestSerializer(request.user, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(CustomerProfileSerializer(request.user).data, status=200)

    @extend_schema(
        tags=["auth_customer"],
        request=CustomerProfileUpdateRequestSerializer,
        responses={200: CustomerProfileSerializer},
        description="Customer profilini qisman update qiladi."
    )
    def patch(self, request):
        ser = CustomerProfileUpdateRequestSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(CustomerProfileSerializer(request.user).data, status=200)


class CustomerProfileImageView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        tags=["auth_customer"],
        request=CustomerImageUpdateRequestSerializer,
        responses={200: CustomerMiniSerializer},
        description="Customer rasmni alohida update qiladi (multipart/form-data)."
    )
    def put(self, request):
        ser = CustomerImageUpdateRequestSerializer(request.user, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(CustomerMiniSerializer(request.user).data, status=200)


class CustomerResetPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["auth_customer"],
        request=CustomerResetPasswordRequestSerializer,
        responses={200: MessageSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Customer reset password. RESET OTP verified bo‘lishi shart."
    )
    def post(self, request):
        ser = CustomerResetPasswordRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        email = ser.validated_data["email"]
        password = ser.validated_data["password"]

        user = Customer.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "Customer topilmadi."}, status=400)

        if not user.is_email_verified:
            return Response({"detail": "Email tasdiqlanmagan."}, status=400)

        user.set_password(password)
        user.save(update_fields=["password", "updated_at"])
        return Response({"message": "Password updated successfully"}, status=200)

#
# class CustomerDetailView(APIView):
#     """
#     GET /api/customer/<id>/
#     - Customer token bo‘lsa: faqat o‘zini ko‘ra oladi
#     - Staff token bo‘lsa: faqat order orqali bog‘langan bo‘lsa ko‘ra oladi (staff app + orders app bo‘lganda)
#     """
#     authentication_classes = [CustomerJWTAuthentication, get_staff_authentication()]
#     permission_classes = [IsAuthenticated]
#
#     @extend_schema(
#         tags=["customers"],
#         responses={200: CustomerMiniSerializer, 403: OpenApiResponse(description="Forbidden")},
#         description="Customer mini detail (first_name, last_name, image). Self yoki order-participant staff."
#     )
#     def get(self, request, id: int):
#         target = get_object_or_404(Customer, id=id)
#
#         # 1) Customer o‘zi
#         if request.user.__class__.__name__ == "Customer":
#             if request.user.id != target.id:
#                 return Response({"detail": "Forbidden"}, status=403)
#             return Response(CustomerMiniSerializer(target).data, status=200)
#
#         # 2) Staff bo‘lsa: order orqali bog‘langanmi?
#         if request.user.__class__.__name__ == "Staff":
#             try:
#                 from orders.models import Order  # type: ignore
#             except Exception:
#                 return Response({"detail": "Orders app not configured yet."}, status=500)
#
#             ok = Order.objects.filter(customer_id=target.id, staff_id=request.user.id).exists()
#             if not ok:
#                 return Response({"detail": "Forbidden"}, status=403)
#             return Response(CustomerMiniSerializer(target).data, status=200)
#
#         return Response({"detail": "Forbidden"}, status=403)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import DeleteAccountSerializer
from auth_customer.authentication import CustomerJWTAuthentication
from .permissions import IsCustomer


class CustomerDeleteAccountView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        tags=["auth_customer"],
        request=DeleteAccountSerializer,
        responses={
            200: OpenApiResponse(description="Customer account deleted"),
            400: OpenApiResponse(description="Password invalid"),
            401: OpenApiResponse(description="Unauthorized"),
        },
        description="Customer o'z accountini parol bilan tasdiqlab o'chiradi."
    )
    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = request.user

        # Agar media/rasm yoki related cleanup bo‘lsa shu yerda qilinadi

        user.delete()
        return Response({"message": "Account o'chirildi"}, status=status.HTTP_200_OK)
