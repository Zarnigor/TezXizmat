from django.db import models
from django.utils import timezone

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        STARTED = "STARTED", "Started"
        COMPLETED_BY_STAFF = "COMPLETED_BY_STAFF", "Completed by staff"
        COMPLETED_BY_CUSTOMER = "COMPLETED_BY_CUSTOMER", "Completed by customer"
        CANCELED = "CANCELED", "Canceled"

    customer = models.ForeignKey("customer.Customer", on_delete=models.CASCADE, related_name="orders")
    staff = models.ForeignKey("staff.Staff", on_delete=models.CASCADE, related_name="orders")

    address = models.CharField(max_length=255)
    problem_text = models.TextField()

    status = models.CharField(max_length=40, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(default=timezone.now)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_by_staff_at = models.DateTimeField(null=True, blank=True)
    completed_by_customer_at = models.DateTimeField(null=True, blank=True)

    canceled_at = models.DateTimeField(null=True, blank=True)
    canceled_by = models.CharField(max_length=10, blank=True)  # "customer" | "staff"
    cancel_reason = models.CharField(max_length=255, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    deleted_by_customer = models.BooleanField(default=False)
    deleted_by_staff = models.BooleanField(default=False)

    @property
    def deleted_for_both(self):
        return self.deleted_by_customer and self.deleted_by_staff

    def __str__(self):
        return f"Order #{self.id} {self.status}"
