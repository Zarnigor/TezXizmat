from django.urls import path
from .views import (
    ReviewCreateView,
    StaffReviewsListView,
    MyReviewsListView,
    ReviewDetailView,
)

urlpatterns = [
    path("create/", ReviewCreateView.as_view(), name="review-create"),
    path("staff/<int:staff_id>/", StaffReviewsListView.as_view(), name="staff-reviews"),
    path("my-reviews/", MyReviewsListView.as_view(), name="my-reviews"),
    path("<int:pk>/", ReviewDetailView.as_view(), name="review-detail"),
]
