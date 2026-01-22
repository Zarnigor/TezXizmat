from rest_framework.permissions import BasePermission

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # variant A: token claim / user attribute
        role = getattr(user, "role", None)
        if role == "customer":
            return True

        # variant B: agar request.auth da token bo'lsa (SimpleJWT)
        token = getattr(request, "auth", None)
        if token and getattr(token, "get", None):
            return token.get("role") == "customer"

        return False