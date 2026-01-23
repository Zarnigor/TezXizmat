from django.urls import path
from .views import *

urlpatterns = [
    path('api/auth/customer/send-email/', SendEmailOTPView.as_view()),
    path('api/auth/customer/verify-email/', VerifyEmailView.as_view()),
    path('api/auth/customer/resend-email/', ResendEmailOTPView.as_view()),

    path('api/auth/staff/send-email/', SendEmailOTPView.as_view()),
    path('api/auth/staff/verify-email/', VerifyEmailView.as_view()),
    path('api/auth/staff/resend-email/', ResendEmailOTPView.as_view()),
]
