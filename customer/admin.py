# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
#
# from .models import Customer
#
# @admin.register(Customer)
# class CustomerAdmin(BaseUserAdmin):
#     ordering = ("id",)
#     list_display = ("id", "email", "first_name", "last_name", "is_active", "created_at")
#     search_fields = ("email", "first_name", "last_name")
#     readonly_fields = ("created_at",)
#
#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         ("Personal info", {"fields": ("first_name", "last_name", "image")}),
#         ("Status", {"fields": ("is_active", "is_email_verified", "is_superuser")}),
#         ("Permissions", {"fields": ("groups", "user_permissions")}),
#         ("Dates", {"fields": ("created_at",)}),
#     )
#
#     add_fieldsets = (
#         (None, {
#             "classes": ("wide",),
#             "fields": ("email", "first_name", "last_name", "password1", "password2"),
#         }),
#     )
