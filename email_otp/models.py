import uuid
from django.db import models
from django.utils import timezone


class EmailOTP(models.Model):
    PURPOSE_VERIFY = "VERIFY"
    PURPOSE_RESET = "RESET"
    PURPOSE_CHOICES = [
        (PURPOSE_VERIFY, "Verify email"),
        (PURPOSE_RESET, "Reset password"),
    ]

    STATE_SENT = "SENT"
    STATE_VERIFIED = "VERIFIED"
    STATE_CHOICES = [
        (STATE_SENT, "Sent"),
        (STATE_VERIFIED, "Verified"),
    ]

    ACTOR_CUSTOMER = "CUSTOMER"
    ACTOR_STAFF = "STAFF"
    ACTOR_CHOICES = [
        (ACTOR_CUSTOMER, "Customer"),
        (ACTOR_STAFF, "Staff"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(db_index=True)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    actor = models.CharField(max_length=10, choices=ACTOR_CHOICES)

    code = models.CharField(max_length=10)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default=STATE_SENT)

    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "actor", "purpose"],
                name="uniq_email_actor_purpose_otp"
            )
        ]
        indexes = [
            models.Index(fields=["email", "actor", "purpose"]),
            models.Index(fields=["email", "actor"]),
        ]

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.email} {self.actor} {self.purpose} {self.state}"
