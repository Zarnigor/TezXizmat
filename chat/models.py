from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class ChatRoom(models.Model):
    """
    1 customer + 1 staff = 1 chat room
    order optional (nullable)
    """
    # Order endi majburiy emas, lekin API response'da order_id qaytishi uchun qoldiramiz
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_rooms",
    )

    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.CASCADE,
        related_name="chat_rooms",
    )
    staff = models.ForeignKey(
        "staff.Staff",
        on_delete=models.CASCADE,
        related_name="chat_rooms",
    )

    deleted_by_customer = models.BooleanField(default=False)
    deleted_by_staff = models.BooleanField(default=False)

    # unread hisoblash uchun eng sodda va ishlaydigan yo‘l:
    customer_last_read_at = models.DateTimeField(null=True, blank=True)
    staff_last_read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "staff"],
                name="uniq_room_customer_staff",
            )
        ]

    def __str__(self):
        return f"Room(customer={self.customer_id}, staff={self.staff_id})"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")

    sender_customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sent_messages",
    )
    sender_staff = models.ForeignKey(
        "staff.Staff",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sent_messages",
    )

    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def clean(self):
        # faqat bittasi set bo‘lsin
        if bool(self.sender_customer_id) == bool(self.sender_staff_id):
            raise ValidationError("Exactly one of sender_customer or sender_staff must be set.")

    @property
    def sender_type(self):
        if self.sender_customer_id:
            return "customer"
        if self.sender_staff_id:
            return "staff"
        return None
