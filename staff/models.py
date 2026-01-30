from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils import timezone

from .managers import StaffManager

class Staff(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True, db_index=True)
    image = models.ImageField(upload_to="staff/", null=True, blank=True)

    profession = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    skills_text = models.TextField(blank=True)
    price_text = models.CharField(max_length=200, blank=True)
    free_time_text = models.CharField(max_length=200, blank=True)

    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ FIX: unique related_name
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="staff_set",
        related_query_name="staff",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="staff_permission_set",
        related_query_name="staff",
    )

    objects = StaffManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "profession"]

    def __str__(self):
        return self.email
