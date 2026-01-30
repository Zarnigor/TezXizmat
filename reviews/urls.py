from django.urls import path
from .views import ReviewCreateView, StaffReviewsListView, MyReviewsView, ReviewDetailView, StaffMyReviewsView

urlpatterns = [
    path("", ReviewCreateView.as_view()),
    path("staff/<int:staff_id>/", StaffReviewsListView.as_view()),
    path("customer/my/", MyReviewsView.as_view()),
    path("<int:id>/", ReviewDetailView.as_view()),
    path("staff/my/", StaffMyReviewsView.as_view()),
]
