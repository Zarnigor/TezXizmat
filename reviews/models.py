from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Review(models.Model):
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="review",
    )
    staff = models.ForeignKey(
        "staff.Staff",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(blank=True)  # optional

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Review {self.id} order={self.order_id} stars={self.stars}"
