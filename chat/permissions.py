from rest_framework.permissions import BasePermission


class IsChatParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.__class__.__name__ == "Customer":
            return obj.customer_id == user.id
        if user.__class__.__name__ == "Staff":
            return obj.staff_id == user.id
        return False
