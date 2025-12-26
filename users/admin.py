# users/admin.py
from django.contrib import admin
from django.utils.crypto import get_random_string
from .models import User

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone', 'role', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('role', 'is_active')
    ordering = ('id',)

    fields = ('first_name', 'last_name', 'email', 'phone', 'role', 'is_active')

    def save_model(self, request, obj, form, change):
        """
        Admin orqali yangi foydalanuvchi yaratilganda avtomatik parol berish.
        """
        if not change and not obj.pk:
            random_password = get_random_string(length=12)
            obj.set_password(random_password)
            obj.created_by = request.user
            obj.is_active = False
        super().save_model(request, obj, form, change)
