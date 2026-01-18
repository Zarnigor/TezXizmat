# staff/authentication.py
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError
from .models import Staff


class StaffJWTAuthentication(BaseAuthentication):
    """
    Staff token:
      - role = "staff"
      - staff_id = <id>
    """
    keyword = "Bearer"

    def authenticate(self, request):
        header = request.headers.get("Authorization")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        raw_token = parts[1]
        token_backend = TokenBackend(
            algorithm=settings.SIMPLE_JWT.get("ALGORITHM", "HS256"),
            signing_key=settings.SIMPLE_JWT.get("SIGNING_KEY", settings.SECRET_KEY),
            verifying_key=settings.SIMPLE_JWT.get("VERIFYING_KEY", None),
            audience=settings.SIMPLE_JWT.get("AUDIENCE", None),
            issuer=settings.SIMPLE_JWT.get("ISSUER", None),
            jwk_url=settings.SIMPLE_JWT.get("JWK_URL", None),
        )

        try:
            payload = token_backend.decode(raw_token, verify=True)
        except TokenError:
            raise AuthenticationFailed("Invalid token")

        if payload.get("role") != "staff":
            raise AuthenticationFailed("Staff token required")

        staff_id = payload.get("staff_id")
        if not staff_id:
            raise AuthenticationFailed("Invalid staff token")

        try:
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            raise AuthenticationFailed("Staff not found")

        if not staff.is_active:
            raise AuthenticationFailed("Staff is not active (verify email)")

        return (staff, payload)
