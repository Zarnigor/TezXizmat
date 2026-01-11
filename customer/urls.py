from django.urls import path
from .views import *

urlpatterns = [
    path('send-email/', SendEmailOTPView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('profile/update/', ProfileUpdateView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
]
