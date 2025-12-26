from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserViewSet,
    EmailVerifyView,
    LoginSendEmailView
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/email-verify-token/', EmailVerifyView.as_view(), name='email-verify'),
    path('auth/login-send-sms/', LoginSendEmailView.as_view(), name='login-send-sms'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
