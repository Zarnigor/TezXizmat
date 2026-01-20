from django.urls import path
from .views import (
    OrderCreateView,
    CustomerOrdersView,
    StaffOrdersView,
    OrderDetailView,
    OrderAcceptView,
    OrderCompleteView,
    OrderCancelView,
)

urlpatterns = [
    path("create/", OrderCreateView.as_view()),
    path("customer-orders/", CustomerOrdersView.as_view()),
    path("staff-orders/", StaffOrdersView.as_view()),
    path("<int:pk>/", OrderDetailView.as_view()),
    path("<int:pk>/accept/", OrderAcceptView.as_view()),
    path("<int:pk>/complete/", OrderCompleteView.as_view()),
    path("<int:pk>/cancel/", OrderCancelView.as_view()),
]
