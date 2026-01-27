from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from customer.models import Customer
from staff.models import Staff
from rest_framework.response import Response
from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderListSerializer,
    OrderDetailSerializer, OrderActionSerializer,
)
from .permissions import IsCustomer, IsStaff, IsOrderParticipant

class OrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = OrderCreateSerializer

    def get_serializer_context(self):
        return {"request": self.request}


class CustomerOrdersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        customer = self.request.user
        return Order.objects.filter(customer=customer).order_by("-created_at")


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from staff.authentication import StaffJWTAuthentication
from .permissions import IsStaff  # sizda bor

class StaffOrdersView(generics.ListAPIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaff]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        staff = self.request.user
        return Order.objects.filter(staff=staff).order_by("-created_at")


class OrderAcceptView(generics.UpdateAPIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaff]
    queryset = Order.objects.select_related("customer", "staff")
    serializer_class = OrderActionSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        staff = request.user

        if order.staff_id != staff.id:
            raise PermissionDenied("Bu order sizga tegishli emas")

        if order.status != Order.Status.PENDING:
            raise ValidationError("Order qabul qilib bo‘lmaydi")

        order.status = Order.Status.ACCEPTED
        order.accepted_at = timezone.now()
        order.save(update_fields=["status", "accepted_at", "updated_at"])

        return Response(OrderDetailSerializer(order).data, status=200)


class OrderCompleteView(generics.UpdateAPIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaff]
    queryset = Order.objects.select_related("customer", "staff")
    serializer_class = OrderActionSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        staff = request.user

        if order.staff_id != staff.id:
            raise PermissionDenied("Bu order sizga tegishli emas")

        if order.status != Order.Status.ACCEPTED:
            raise ValidationError("Order tugatib bo‘lmaydi")

        order.status = Order.Status.COMPLETED
        order.completed_at = timezone.now()
        order.save(update_fields=["status", "completed_at", "updated_at"])

        return Response(OrderDetailSerializer(order).data, status=200)


class OrderCancelView(generics.UpdateAPIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOrderParticipant]
    queryset = Order.objects.select_related("customer", "staff")
    serializer_class = OrderActionSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        order = self.get_object()  # permission shu yerda ishlaydi
        user = request.user

        # 🧠 Kim cancel qilyapti?
        #if order.customer.id == user.id:
            #canceled_by = "customer"
        if order.staff.id == user.id:
            canceled_by = "staff"
        else:
            # amalda bu holatga tushmaydi, permission sabab
            raise PermissionDenied("Bu order sizga tegishli emas")

        # ❌ state tekshiruvlar
        if order.status == Order.Status.COMPLETED:
            raise ValidationError("Yakunlangan order bekor qilinmaydi")

        if order.status == Order.Status.CANCELED:
            raise ValidationError("Order allaqachon bekor qilingan")

        order.status = Order.Status.CANCELED
        order.canceled_at = timezone.now()
        #order.canceled_by = user
        order.save(update_fields=["status", "canceled_at", "updated_at"])

        return Response({**OrderDetailSerializer(order).data})


class OrderDetailView(generics.RetrieveAPIView): 
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOrderParticipant]
    # http_method_names = ["put"]
    serializer_class = OrderDetailSerializer
    queryset = Order.objects.all()

