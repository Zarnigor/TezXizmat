from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Review
from .serializers import (
    ReviewCreateSerializer,
    ReviewListSerializer,
    ReviewDetailSerializer,
)
from .permissions import IsCustomer

class ReviewCreateView(generics.CreateAPIView):
    """
    POST /api/reviews/create/
    Customer staffga rating(1-5) va optional comment beradi.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class StaffReviewsListView(generics.ListAPIView):
    """
    GET /api/reviews/staff/<staff_id>/
    Tanlangan staff bo‘yicha barcha reviewlar.
    """
    serializer_class = ReviewListSerializer
    permission_classes = [IsAuthenticated]  # xohlasangiz AllowAny qiling

    def get_queryset(self):
        staff_id = self.kwargs["staff_id"]
        return Review.objects.filter(staff_id=staff_id).select_related("staff")


class MyReviewsListView(generics.ListAPIView):
    """
    GET /api/reviews/my-reviews/
    Hozirgi user (customer) bergan reviewlar.
    """
    serializer_class = ReviewListSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Review.objects.filter(customer=self.request.user).select_related("staff")


class ReviewDetailView(generics.RetrieveAPIView):
    """
    GET /api/reviews/<id>/
    Bitta review detail.
    """
    queryset = Review.objects.all().select_related("customer", "staff")
    serializer_class = ReviewDetailSerializer
    permission_classes = [IsAuthenticated]
