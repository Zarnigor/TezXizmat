from django.urls import path
from .views import ReviewCreateView, StaffReviewsListView, MyReviewsView, ReviewDetailView

urlpatterns = [
    path("reviews/", ReviewCreateView.as_view()),
    path("reviews/staff/<int:staff_id>/", StaffReviewsListView.as_view()),
    path("reviews/my/", MyReviewsView.as_view()),
    path("reviews/<int:id>/", ReviewDetailView.as_view()),
]
