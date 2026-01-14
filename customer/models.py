from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email majburiy")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class Customer(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomerManager()

    USERNAME_FIELD = 'email'


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
