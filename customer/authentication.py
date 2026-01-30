from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

Customer = get_user_model()

class CustomerJWTAuthentication(JWTAuthentication):
    """
    DRF ketma-ket authenticatorlarda ishlatish uchun 'muloyim' behavior:
    - header yo‘q => None (error emas)
    - token boshqa user_type bo‘lsa => None (error emas)
    - token buzilgan / expired => AuthenticationFailed (401)
    """

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except InvalidToken as e:
            raise AuthenticationFailed("Invalid or expired token") from e

        if validated_token.get("user_type") != "customer":
            return None

        user = self.get_user(validated_token)
        return (user, validated_token)

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        if not user_id:
            raise AuthenticationFailed("Token missing user_id")

        try:
            user = Customer.objects.get(id=user_id)
        except Customer.DoesNotExist as e:
            raise AuthenticationFailed("User not found") from e

        if not user.is_active:
            raise AuthenticationFailed("User inactive")

        return user
