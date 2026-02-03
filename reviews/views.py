from customer.authentication import CustomerJWTAuthentication
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from orders.models import Order
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from staff.authentication import StaffJWTAuthentication

from .models import Review
from .serializers import ReviewCreateRequestSerializer
from .serializers import ReviewSerializer


class ReviewCreateView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["reviews"],
        request=ReviewCreateRequestSerializer,
        responses={201: ReviewSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Customer staffga baho qo‘shadi. Shartlar: order COMPLETED_BY_CUSTOMER va 1 order = 1 review."
    )
    def post(self, request):
        if request.user.__class__.__name__ != "Customer":
            return Response({"detail": "Customer token required"}, status=403)

        ser = ReviewCreateRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        order = get_object_or_404(Order, id=ser.validated_data["order_id"])

        # order egasi bo‘lishi shart
        if order.customer_id != request.user.id:
            return Response({"detail": "Bu order sizga tegishli emas."}, status=403)

        # faqat customer tasdiqlaganidan keyin
        if order.status != Order.Status.COMPLETED_BY_CUSTOMER:
            return Response(
                {"detail": "Baho faqat COMPLETED_BY_CUSTOMER bo‘lganda yoziladi (customer tasdiqlagandan keyin)."},
                status=400
            )

        # 1 order = 1 review (OneToOne) — oldin tekshiramiz (tezroq xabar uchun)
        if hasattr(order, "review"):
            return Response({"detail": "Bu order uchun review allaqachon yozilgan."}, status=400)

        try:
            review = Review.objects.create(
                order=order,
                staff=order.staff,
                customer=request.user,
                stars=ser.validated_data["stars"],
                text=(ser.validated_data.get("text") or "").strip(),
            )
        except IntegrityError:
            # race condition bo‘lsa ham (2 marta post) shu yerda ushlaydi
            return Response({"detail": "Bu order uchun review allaqachon yozilgan."}, status=400)

        return Response(ReviewSerializer(review).data, status=201)


class StaffReviewsListView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["reviews"],
        responses={200: ReviewSerializer(many=True)},
        description="Tanlangan staffga berilgan barcha baholar."
    )
    def get(self, request, staff_id: int):
        qs = Review.objects.filter(staff_id=staff_id).order_by("-created_at")
        return Response(ReviewSerializer(qs, many=True).data, status=200)


class MyReviewsView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["reviews"],
        responses={200: ReviewSerializer(many=True)},
        description="Hozirgi Customer tomonidan berilgan baholar."
    )
    def get(self, request):
        if request.user.__class__.__name__ != "Customer":
            return Response({"detail": "Customer token required"}, status=403)

        qs = Review.objects.filter(customer=request.user).order_by("-created_at")
        return Response(ReviewSerializer(qs, many=True).data, status=200)


class ReviewDetailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["reviews"],
        responses={200: ReviewSerializer, 404: OpenApiResponse(description="Not found")},
        description="Bitta review tafsiloti (public)."
    )
    def get(self, request, id: int):
        review = get_object_or_404(Review, id=id)
        return Response(ReviewSerializer(review).data, status=200)



class StaffMyReviewsView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["reviews"],
        responses={
            200: ReviewSerializer(many=True),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Staff token required"),
        },
        description="Hozirgi staffga yozilgan barcha baholar (my received reviews)."
    )
    def get(self, request):
        # Auth class token staff bo‘lmasa request.user None bo‘lishi mumkin,
        # IsAuthenticated buni to‘xtatadi, lekin qo‘shimcha xavfsizlik:
        if request.user.__class__.__name__ != "Staff":
            return Response({"detail": "Staff token required"}, status=403)

        qs = (
            Review.objects
            .select_related("customer", "staff")
            .filter(staff=request.user)
            .order_by("-created_at")
        )

        return Response(ReviewSerializer(qs, many=True).data, status=200)


class ReviewDeleteView(APIView):
    """
    Customer faqat o'zi yozgan reviewni o‘chirishi mumkin
    """
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, id: int):
        # faqat customer token
        if request.user.__class__.__name__ != "Customer":
            return Response(
                {"detail": "Customer token required"},
                status=403
            )

        review = get_object_or_404(Review, id=id)

        # o‘ziga tegishlimi?
        if review.customer_id != request.user.id:
            return Response(
                {"detail": "You can delete only your own review"},
                status=403
            )

        review.delete()
        return Response(
            {"detail": "Review deleted successfully"},
            status=204
        )

