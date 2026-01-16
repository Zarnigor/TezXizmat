from django.db import models
from django.utils import timezone
from datetime import timedelta

class EmailOTP(models.Model):
    PURPOSE_VERIFY = 'VERIFY'
    PURPOSE_RESET = 'RESET'

    PURPOSE_CHOICES = (
        (PURPOSE_VERIFY, 'Verify email'),
        (PURPOSE_RESET, 'Reset password'),
    )

    STATE_SEND = 'SEND'
    STATE_VERIFIED = 'VERIFIED'
    STATE_USED = 'USED'

    STATE_CHOICES = (
        (STATE_SEND, 'Send'),
        (STATE_VERIFIED, 'Verified'),
        (STATE_USED, 'Used'),
    )

    email = models.EmailField()
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    state = models.CharField(
        max_length=10,
        choices=STATE_CHOICES,
        default=STATE_SEND
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=1)
