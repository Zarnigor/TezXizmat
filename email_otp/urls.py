from django.urls import path
from .views import *

urlpatterns = [
    path('customer/send-email/', SendEmailOTPView.as_view()),
    path('customer/verify-email/', VerifyEmailView.as_view()),
    path('customer/resend-email/', ResendEmailOTPView.as_view()),

    path('staff/send-email/', SendEmailOTPView.as_view()),
    path('staff/verify-email/', VerifyEmailView.as_view()),
    path('staff/resend-email/', ResendEmailOTPView.as_view()),
]