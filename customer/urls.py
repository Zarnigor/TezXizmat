from django.urls import path
from .views import (
    CustomerRegisterView, CustomerLoginView, CustomerLogoutView,
    CustomerTokenRefreshView, CustomerProfileView, CustomerProfileImageView,
    CustomerResetPasswordView, CustomerDeleteAccountView,
)

urlpatterns = [
    path("register/", CustomerRegisterView.as_view()),
    path("login/", CustomerLoginView.as_view()),
    path("logout/", CustomerLogoutView.as_view()),
    path("token/refresh/", CustomerTokenRefreshView.as_view()),
    path("profile/", CustomerProfileView.as_view()),
    path("profile/image/", CustomerProfileImageView.as_view()),
    path("reset-password/", CustomerResetPasswordView.as_view()),
    path("delete/", CustomerDeleteAccountView.as_view())
]
