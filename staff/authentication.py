# staff/authentication.py
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError, TokenBackendError
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
        if len(parts) != 2 or parts[0].lower() != self.keyword.lower():
            return None

        raw_token = parts[1]

        simple_jwt = getattr(settings, "SIMPLE_JWT", {})

        token_backend = TokenBackend(
            algorithm=simple_jwt.get("ALGORITHM", "HS256"),
            signing_key=simple_jwt.get("SIGNING_KEY", settings.SECRET_KEY),
            verifying_key=simple_jwt.get("VERIFYING_KEY", None),
            audience=simple_jwt.get("AUDIENCE", None),
            issuer=simple_jwt.get("ISSUER", None),
            jwk_url=simple_jwt.get("JWK_URL", None),
        )

        try:
            payload = token_backend.decode(raw_token, verify=True)
        except (TokenError, TokenBackendError):
            raise AuthenticationFailed("Invalid token")

        if payload.get("role") != "staff":
            raise AuthenticationFailed("Staff token required")

        staff_id = payload.get("staff_id")
        if not staff_id:
            raise AuthenticationFailed("Invalid staff token (staff_id missing)")

        try:
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            raise AuthenticationFailed("Staff not found")

        if not staff.is_active:
            raise AuthenticationFailed("Staff is not active (verify email)")

        return (staff, payload)
