from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        scope["user"] = AnonymousUser()

        headers = dict(scope.get("headers") or [])
        auth = headers.get(b"authorization", b"").decode()

        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
            user = await self._get_user_from_token(token)
            if user is not None:
                scope["user"] = user

        return await super().__call__(scope, receive, send)

    async def _get_user_from_token(self, token: str):
        """
        Sync jwt validation + db fetch, lekin async wrapper bilan.
        """
        from asgiref.sync import sync_to_async

        def _sync():
            jwt_auth = JWTAuthentication()
            validated = jwt_auth.get_validated_token(token)

            user_type = validated.get("user_type")
            user_id = validated.get("user_id")
            if not user_type or not user_id:
                return None

            if user_type == "customer":
                from customer.models import Customer
                return Customer.objects.filter(id=user_id, is_active=True).first()
            if user_type == "staff":
                from staff.models import Staff
                return Staff.objects.filter(id=user_id, is_active=True).first()
            return None

        return await sync_to_async(_sync)()
