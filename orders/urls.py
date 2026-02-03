from django.urls import path
from .views import (
    OrderCreateView,
    CustomerOrdersView,
    StaffOrdersView,
    OrderDetailView,
    OrderAcceptView,
    OrderStartView,
    OrderCompleteByStaffView,
    OrderCompleteByCustomerView,
    OrderCancelView,
)

urlpatterns = [
    path("create/", OrderCreateView.as_view()),
    path("customer-orders/", CustomerOrdersView.as_view()),
    path("staff-orders/", StaffOrdersView.as_view()),
    path("<int:pk>/", OrderDetailView.as_view()),
    path("<int:id>/accept/", OrderAcceptView.as_view()),
    path("<int:id>/start/", OrderStartView.as_view()),
    path("<int:id>/complete-by-staff/", OrderCompleteByStaffView.as_view()),
    path("<int:id>/confirm-completion/", OrderCompleteByCustomerView.as_view()),
    path("<int:id>/cancel/", OrderCancelView.as_view()),
]
