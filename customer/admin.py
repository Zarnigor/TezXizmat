# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import Customer, EmailVerification
#
#
# class CustomUserAdmin(UserAdmin):
#     list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_email_verified')
#     list_filter = ('is_staff', 'is_active', 'is_email_verified')
#     search_fields = ('email', 'first_name', 'last_name')
#     ordering = ('email',)
#
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name', 'profile_image', 'phone_number')}),
#         ('Permissions',
#          {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_email_verified', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
#     )
#
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')}
#          ),
#     )
#
#     readonly_fields = ('created_at', 'updated_at')
#
#
# @admin.register(EmailVerification)
# class EmailVerificationAdmin(admin.ModelAdmin):
#     list_display = ('customer', 'otp', 'created_at', 'expires_at', 'is_used')
#     list_filter = ('is_used', 'created_at')
#     search_fields = ('customer__email', 'otp')
#     readonly_fields = ('created_at',)
#
#
# admin.site.register(Customer, CustomUserAdmin)