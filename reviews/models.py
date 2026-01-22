from django.db import models
from django.conf import settings

class Review(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    staff = models.ForeignKey(
        "staff.Staff", on_delete=models.CASCADE, related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField()  # 1..5
    comment = models.TextField(blank=True, null=True)  # optional

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["customer", "staff"], name="uniq_customer_staff_review")
        ]

    def __str__(self):
        return f"{self.customer_id} -> {self.staff_id} ({self.rating})"
