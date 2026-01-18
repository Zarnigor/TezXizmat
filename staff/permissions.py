# staff/permissions.py
from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user) and request.user.__class__.__name__ == "Staff"
