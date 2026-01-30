from django.urls import path
from .views import (
    CustomerSendEmailView,
    CustomerResendEmailView,
    CustomerVerifyEmailView,
    StaffSendEmailView,
    StaffResendEmailView,
    StaffVerifyEmailView,
)

urlpatterns = [
    # customer
    path("api/auth/customer/send-email/", CustomerSendEmailView.as_view()),
    path("api/auth/customer/resend-email/", CustomerResendEmailView.as_view()),
    path("api/auth/customer/verify-email/", CustomerVerifyEmailView.as_view()),

    # staff
    path("api/auth/staff/send-email/", StaffSendEmailView.as_view()),
    path("api/auth/staff/resend-email/", StaffResendEmailView.as_view()),
    path("api/auth/staff/verify-email/", StaffVerifyEmailView.as_view()),
]
