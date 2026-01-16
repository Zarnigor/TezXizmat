from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class StaffManager(BaseUserManager):
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


class Staff(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    image = models.ImageField(upload_to="staff/", blank=True, null=True)
    profession = models.CharField(max_length=255)

    comments = models.TextField(blank=True)
    description = models.TextField(blank=True)
    skills = models.TextField()

    price = models.CharField(max_length=100)
    free_time = models.CharField(max_length=255)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = StaffManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email
