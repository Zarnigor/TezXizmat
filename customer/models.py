from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.base_user import BaseUserManager

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
    image = models.ImageField(upload_to='customers/', null=True, blank=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomerManager()

    USERNAME_FIELD = 'email'


class EmailOTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)  # 🔥 MUHIM
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return now() > self.created_at + timedelta(seconds=60)
