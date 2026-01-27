from rest_framework.permissions import BasePermission
from customer.models import Customer
from staff.models import Staff


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, Customer)


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, Staff)


class IsOrderParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user or obj.staff == request.user
