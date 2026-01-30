from rest_framework.permissions import BasePermission

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.__class__.__name__ == "Customer")
