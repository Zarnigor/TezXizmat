from rest_framework.permissions import BasePermission
from customer.models import Customer
from staff.models import Staff


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return Customer.objects.filter(user=request.user).exists()


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return Staff.objects.filter(user=request.user).exists()


class IsOrderParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.customer.user == request.user
            or obj.staff.user == request.user
        )
