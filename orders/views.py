from customer.authentication import CustomerJWTAuthentication
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from orders.models import Order
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from staff.authentication import StaffJWTAuthentication
from staff.models import Staff

from .models import Order
from .permissions import IsOrderParticipant
from .serializers import (
    OrderCreateRequestSerializer,
    OrderCancelRequestSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)


class OrderCreateView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["orders"],
        request=OrderCreateRequestSerializer,
        responses={201: OrderDetailSerializer, 400: OpenApiResponse(description="Validation error")},
        description="Customer yangi order yaratadi."
    )
    def post(self, request):
        if request.user.__class__.__name__ != "Customer":
            return Response({"detail": "Customer token required"}, status=403)

        ser = OrderCreateRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        staff = get_object_or_404(Staff, id=ser.validated_data["staff_id"])

        order = Order.objects.create(
            customer=request.user,
            staff=staff,
            address=ser.validated_data["address"],
            problem_text=ser.validated_data["problem_text"],
        )
        return Response(OrderDetailSerializer(order).data, status=201)


class CustomerOrdersView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["orders"],
        responses={200: OrderListSerializer(many=True)},
        description="Customer o‘z orderlarini ko‘radi."
    )
    def get(self, request):
        if request.user.__class__.__name__ != "Customer":
            return Response({"detail": "Customer token required"}, status=403)

        qs = Order.objects.filter(customer=request.user).order_by("-created_at")
        return Response(OrderListSerializer(qs, many=True).data, status=200)


class StaffOrdersView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["orders"],
        responses={200: OrderListSerializer(many=True)},
        description="Staff o‘ziga biriktirilgan orderlarni ko‘radi."
    )
    def get(self, request):
        if request.user.__class__.__name__ != "Staff":
            return Response({"detail": "Staff token required"}, status=403)

        qs = Order.objects.filter(staff=request.user).order_by("-created_at")
        return Response(OrderListSerializer(qs, many=True).data, status=200)


class OrderDetailView(APIView):
    authentication_classes = [CustomerJWTAuthentication, StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOrderParticipant]

    @extend_schema(
        tags=["orders"],
        responses={200: OrderDetailSerializer, 403: OpenApiResponse(description="Forbidden")},
        description="Order detail (faqat participant)."
    )
    def get(self, request, id: int):
        order = get_object_or_404(Order, id=id)
        self.check_object_permissions(request, order)
        return Response(OrderDetailSerializer(order).data, status=200)


class OrderAcceptView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOrderParticipant]

    @extend_schema(
        tags=["orders"],
        responses={200: OrderDetailSerializer, 400: OpenApiResponse(description="Invalid state")},
        description="Staff orderni ACCEPTED ga o‘tkazadi."
    )
    def put(self, request, id: int):
        if request.user.__class__.__name__ != "Staff":
            return Response({"detail": "Staff token required"}, status=403)

        order = get_object_or_404(Order, id=id)
        self.check_object_permissions(request, order)

        if order.status != Order.Status.PENDING:
            return Response({"detail": "Order faqat PENDING bo‘lsa qabul qilinadi."}, status=400)

        order.status = Order.Status.ACCEPTED
        # from chat.models import ChatRoom
        # ChatRoom.objects.get_or_create(
        #     order=order,
        #     defaults={"customer": order.customer, "staff": order.staff},
        # )

        order.accepted_at = timezone.now()
        order.save(update_fields=["status", "accepted_at", "updated_at"])
        return Response(OrderDetailSerializer(order).data, status=200)


class OrderStartView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOrderParticipant]

    @extend_schema(
        tags=["orders"],
        responses={200: OrderDetailSerializer, 400: OpenApiResponse(description="Invalid state")},
        description="Staff orderni STARTED ga o‘tkazadi."
    )
    def put(self, request, id: int):
        if request.user.__class__.__name__ != "Staff":
            return Response({"detail": "Staff token required"}, status=403)

        order = get_object_or_404(Order, id=id)
        self.check_object_permissions(request, order)

        if order.status != Order.Status.ACCEPTED:
            return Response({"detail": "Order faqat ACCEPTED bo‘lsa START bo‘ladi."}, status=400)

        order.status = Order.Status.STARTED
        order.started_at = timezone.now()
        order.save(update_fields=["status", "started_at", "updated_at"])
        return Response(OrderDetailSerializer(order).data, status=200)


class OrderCompleteByStaffView(APIView):
    authentication_classes = [StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOrderParticipant]

    @extend_schema(
        tags=["orders"],
        responses={200: OrderDetailSerializer, 400: OpenApiResponse(description="Invalid state")},
        description="Staff orderni COMPLETED_BY_STAFF ga o‘tkazadi."
    )
    def put(self, request, id: int):
        if request.user.__class__.__name__ != "Staff":
            return Response({"detail": "Staff token required"}, status=403)

        order = get_object_or_404(Order, id=id)
        self.check_object_permissions(request, order)

        if order.status != Order.Status.STARTED:
            return Response({"detail": "Order faqat STARTED bo‘lsa staff tugata oladi."}, status=400)

        order.status = Order.Status.COMPLETED_BY_STAFF
        order.completed_by_staff_at = timezone.now()
        order.save(update_fields=["status", "completed_by_staff_at", "updated_at"])
        return Response(OrderDetailSerializer(order).data, status=200)


class OrderCompleteByCustomerView(APIView):
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOrderParticipant]

    @extend_schema(
        tags=["orders"],
        responses={200: OrderDetailSerializer, 400: OpenApiResponse(description="Invalid state")},
        description="Customer orderni COMPLETED_BY_CUSTOMER ga o‘tkazadi (faqat staff tugatgandan keyin)."
    )
    def put(self, request, id: int):
        if request.user.__class__.__name__ != "Customer":
            return Response({"detail": "Customer token required"}, status=403)

        order = get_object_or_404(Order, id=id)
        self.check_object_permissions(request, order)

        if order.status != Order.Status.COMPLETED_BY_STAFF:
            return Response({"detail": "Order faqat COMPLETED_BY_STAFF bo‘lsa customer yakunlay oladi."}, status=400)

        order.status = Order.Status.COMPLETED_BY_CUSTOMER
        order.completed_by_customer_at = timezone.now()
        order.save(update_fields=["status", "completed_by_customer_at", "updated_at"])
        return Response(OrderDetailSerializer(order).data, status=200)


class OrderCancelView(APIView):
    authentication_classes = [CustomerJWTAuthentication, StaffJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOrderParticipant]

    @extend_schema(
        tags=["orders"],
        request=OrderCancelRequestSerializer,
        responses={200: OrderDetailSerializer, 400: OpenApiResponse(description="Invalid state")},
        description="Orderni bekor qilish (customer yoki staff)."
    )
    def put(self, request, id: int):
        order = get_object_or_404(Order, id=id)
        self.check_object_permissions(request, order)

        # Cancel qoidasi: ikkalasi ham, lekin yakunlangan bo‘lsa bekor bo‘lmaydi
        if order.status in (Order.Status.COMPLETED_BY_STAFF, Order.Status.COMPLETED_BY_CUSTOMER, Order.Status.CANCELED):
            return Response({"detail": "Bu holatda cancel qilib bo‘lmaydi."}, status=400)

        ser = OrderCancelRequestSerializer(data=request.data or {})
        ser.is_valid(raise_exception=True)

        order.status = Order.Status.CANCELED
        order.canceled_at = timezone.now()
        order.cancel_reason = ser.validated_data.get("reason", "") or ""
        order.canceled_by = "customer" if request.user.__class__.__name__ == "Customer" else "staff"
        order.save(update_fields=["status", "canceled_at", "cancel_reason", "canceled_by", "updated_at"])

        return Response(OrderDetailSerializer(order).data, status=200)




class OrderHideView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["orders"],
        request=OrderCancelRequestSerializer,
        responses={200: "Deleted", 400: OpenApiResponse(description="Invalid state")},
        description="Faqat Canceled bo'lgan orderni o'zingizdan o'chirish"
    )
    def delete(self, request, id):
        order = get_object_or_404(Order, id=id)

        # faqat CANCELED bo‘lsa
        if order.status != Order.Status.CANCELED:
            return Response({"detail": "Faqat CANCELED orderni o‘chirish mumkin."}, status=400)

        user_type = request.user.__class__.__name__

        # faqat participant bo‘lsa
        if user_type == "Customer":
            if order.customer_id != request.user.id:
                return Response({"detail": "Bu order sizniki emas."}, status=403)
            order.deleted_by_customer = True

        elif user_type == "Staff":
            if order.staff_id != request.user.id:
                return Response({"detail": "Bu order sizniki emas."}, status=403)
            order.deleted_by_staff = True

        else:
            return Response({"detail": "Noto‘g‘ri user."}, status=403)

        order.save(update_fields=["deleted_by_customer", "deleted_by_staff", "updated_at"])

        return Response({"detail": "Order siz uchun o‘chirildi (yashirildi)."}, status=204)
