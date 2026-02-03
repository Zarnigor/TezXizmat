from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from customer.models import Customer
from staff.models import Staff


@database_sync_to_async
def get_user_from_validated_token(validated_token):
    user_type = validated_token.get("user_type")
    user_id = validated_token.get("user_id")

    if not user_type or not user_id:
        return AnonymousUser()

    try:
        if user_type == "customer":
            return Customer.objects.get(id=user_id)
        if user_type == "staff":
            return Staff.objects.get(id=user_id)
    except (Customer.DoesNotExist, Staff.DoesNotExist):
        return AnonymousUser()

    return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    WebSocket uchun: ws://.../?token=ACCESS_TOKEN
    Tokenni tekshiradi va scope['user'] ni Staff/Customer qilib beradi.
    """

    async def __call__(self, scope, receive, send):
        scope["user"] = AnonymousUser()

        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = None

        # ?token=...
        if "token" in params:
            token = params["token"][0]

        # Agar xohlasangiz: Authorization header'ni ham qo'llab-quvvatlaymiz
        if not token:
            headers = dict(scope.get("headers") or [])
            auth = headers.get(b"authorization")
            if auth:
                try:
                    auth_str = auth.decode()
                    if auth_str.lower().startswith("bearer "):
                        token = auth_str.split(" ", 1)[1].strip()
                except Exception:
                    token = None

        if token:
            jwt_auth = JWTAuthentication()
            try:
                validated = jwt_auth.get_validated_token(token)
                scope["user"] = await get_user_from_validated_token(validated)
            except (InvalidToken, TokenError):
                scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
