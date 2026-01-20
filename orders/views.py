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
    serializer_class = OrderListSerializer

    def get_queryset(self):
        customer = Customer.objects.get(user=self.request.user)
        return Order.objects.filter(customer=customer).order_by("-created_at")


class StaffOrdersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsStaff]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        staff = Staff.objects.get(user=self.request.user)
        return Order.objects.filter(staff=staff).order_by("-created_at")


class OrderAcceptView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsStaff]
    queryset = Order.objects.select_related("customer__user", "staff__user")
    serializer_class = OrderActionSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        staff = Staff.objects.get(user=request.user)

        if order.staff_id != staff.id:
            raise PermissionDenied("Bu order sizga tegishli emas")

        if order.status != Order.Status.PENDING:
            raise ValidationError("Order qabul qilib bo‘lmaydi")

        order.status = Order.Status.ACCEPTED
        order.accepted_at = timezone.now()
        order.save(update_fields=["status", "accepted_at", "updated_at"])

        return Response(OrderDetailSerializer(order).data, status=200)


class OrderCompleteView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsStaff]
    queryset = Order.objects.select_related("customer__user", "staff__user")
    serializer_class = OrderActionSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        staff = Staff.objects.get(user=request.user)

        if order.staff_id != staff.id:
            raise PermissionDenied("Bu order sizga tegishli emas")

        if order.status != Order.Status.ACCEPTED:
            raise ValidationError("Order tugatib bo‘lmaydi")

        order.status = Order.Status.COMPLETED
        order.completed_at = timezone.now()
        order.save(update_fields=["status", "completed_at", "updated_at"])

        return Response(OrderDetailSerializer(order).data, status=200)


class OrderCancelView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsOrderParticipant]
    queryset = Order.objects.select_related("customer__user", "staff__user")
    serializer_class = OrderActionSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        order = self.get_object()  # permission shu yerda ishlaydi
        user = request.user

        # 🧠 Kim cancel qilyapti?
        if order.customer.user_id == user.id:
            canceled_by = "customer"
        elif order.staff.user_id == user.id:
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
        order.canceled_by = user
        order.save(update_fields=["status", "canceled_at", "canceled_by", "updated_at"])

        return Response({
            **OrderDetailSerializer(order).data,
            "canceled_by_role": canceled_by,
        })


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOrderParticipant]
    # http_method_names = ["put"]
    serializer_class = OrderDetailSerializer
    queryset = Order.objects.all()
