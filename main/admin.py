from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Booking


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для пользователей с дополнительными полями"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone', 'is_manager', 'is_staff', 'is_active']
    list_filter = ['is_manager', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('phone', 'is_manager')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('phone', 'is_manager')}),
    )
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Базовая админка для броней (для справки)"""
    list_display = ['date', 'hour', 'table_number', 'user', 'status', 'created_at']
    list_filter = ['status', 'date', 'table_number']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
