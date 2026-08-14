# /var/www/ttennis/main/permissions.py

from rest_framework import permissions
from django.utils import timezone
from .models import Booking


class IsOwnerOrAdmin(permissions.BasePermission):
    """Разрешает доступ только владельцу объекта или администратору"""
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.user == request.user if hasattr(obj, 'user') else obj == request.user


class IsAdminOrManager(permissions.BasePermission):
    """
    Разрешает доступ только администраторам.
    🔥 FIX: Безопасная проверка для AnonymousUser
    """
    def has_permission(self, request, view):
        # 🔥 Сначала проверяем авторизацию
        if not request.user or not request.user.is_authenticated:
            return False
        # 🔥 Безопасное обращение к is_manager через getattr
        return (
            request.user.is_staff or 
            getattr(request.user, 'is_manager', False) or 
            request.user.is_superuser
        )


class CanDeleteBooking(permissions.BasePermission):
    """Проверка: может ли пользователь удалить свою бронь"""
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if (
            request.user.is_staff
            or request.user.is_superuser
            or getattr(request.user, 'is_manager', False)
        ):
            return True

        if obj.user != request.user:
            return False
        from django.conf import settings
        hours_limit = getattr(settings, 'BOOKING_CANCEL_HOURS', 2)
        now = timezone.localtime()
        booking_start = timezone.make_aware(
            timezone.datetime.combine(obj.date, timezone.datetime.min.time().replace(hour=obj.hour))
        )
        time_diff = booking_start - now
        return time_diff.total_seconds() >= hours_limit * 3600


class IsAuthenticatedCreateOnly(permissions.BasePermission):
    """Разрешает создание только авторизованным. Чтение — всем"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
