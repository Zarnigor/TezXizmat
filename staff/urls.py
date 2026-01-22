# staff/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

urlpatterns = [
    # auth staff
    path("api/auth/staff/register/", StaffRegisterView.as_view()),
    path("api/auth/staff/login/", StaffLoginView.as_view()),
    path("api/auth/staff/logout/", StaffLogoutView.as_view()),
    path("api/auth/staff/profile/", StaffProfileView.as_view()),

    # public staff catalog
    path("api/staff/", StaffListView.as_view()),
    path("api/staff/<int:pk>/", StaffDetailView.as_view()),

    path("api/auth/staff/register/", StaffRegisterView.as_view()),
    path("api/auth/staff/profile/", StaffProfileView.as_view()),
    path("api/auth/staff/profile/image/", StaffProfileImageView.as_view()),

    path("api/auth/token/refresh/", TokenRefreshView.as_view())
]
