from django.urls import path
from .views import (
    StaffRegisterView,
    StaffLoginView,
    StaffLogoutView,
    StaffTokenRefreshView,
    StaffProfileView,
    StaffProfileImageView,
    StaffResetPasswordView, StaffDeleteAccountView,
)

urlpatterns = [
    path("register/", StaffRegisterView.as_view()),
    path("login/", StaffLoginView.as_view()),
    path("logout/", StaffLogoutView.as_view()),
    path("token/refresh/", StaffTokenRefreshView.as_view()),
    path("profile/", StaffProfileView.as_view()),
    path("profile/image/", StaffProfileImageView.as_view()),
    path("reset-password/", StaffResetPasswordView.as_view()),
    path("delete/", StaffDeleteAccountView.as_view())
]
