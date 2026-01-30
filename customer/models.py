from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils import timezone

from .managers import CustomerManager

class Customer(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True, db_index=True)
    image = models.ImageField(upload_to="customers/", null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ FIX: unique related_name
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="customer_set",
        related_query_name="customer",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="customer_permission_set",
        related_query_name="customer",
    )

    objects = CustomerManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email
