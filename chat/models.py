from django.db import models
from django.utils import timezone


class ChatRoom(models.Model):
    """
    1 order = 1 chat room
    """
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="chat_room",
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

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Room(order={self.order_id})"


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

    def sender_type(self):
        if self.sender_customer_id:
            return "customer"
        if self.sender_staff_id:
            return "staff"
        return None
