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
    path("orders/", OrderCreateView.as_view()),
    path("orders/customer/", CustomerOrdersView.as_view()),
    path("orders/staff/", StaffOrdersView.as_view()),
    path("orders/<int:id>/", OrderDetailView.as_view()),

    path("orders/<int:id>/accept/", OrderAcceptView.as_view()),
    path("orders/<int:id>/start/", OrderStartView.as_view()),
    path("orders/<int:id>/complete-by-staff/", OrderCompleteByStaffView.as_view()),
    path("orders/<int:id>/confirm-completion/", OrderCompleteByCustomerView.as_view()),
    path("orders/<int:id>/cancel/", OrderCancelView.as_view()),
]
