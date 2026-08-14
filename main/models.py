# /var/www/ttennis/main/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Расширенная модель пользователя.
    🔥 Исправлено: email теперь уникальный
    """
    phone = models.CharField('Телефон', max_length=20, blank=True, null=True)
    is_manager = models.BooleanField('Менеджер', default=False)
    
    # 🔥 Email теперь уникальный
    email = models.EmailField('Email', unique=True)
    
    def __str__(self):
        return self.username or self.email or f'User {self.pk}'
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']


class Booking(models.Model):
    """
    Модель бронирования стола.
    🔥 Исправлено: UniqueConstraint для Django 4+
    """
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает подтверждения'),
        (STATUS_CONFIRMED, 'Подтверждено'),
        (STATUS_CANCELLED, 'Отменено'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name='Пользователь'
    )
    date = models.DateField('Дата', db_index=True)
    hour = models.IntegerField('Время начала (час)', choices=[(i, f'{i:02d}:00') for i in range(8, 24)])
    table_number = models.IntegerField('Номер стола', default=1)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_bookings',
        verbose_name='Подтвердил'
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    def __str__(self):
        return f'Бронь #{self.id} - {self.user.username} - {self.date} {self.hour}:00 - Стол {self.table_number}'
    
    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-date', 'hour', 'table_number']
        # 🔥 Django 4+ стиль для уникальности
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'hour', 'table_number'],
                name='unique_booking_slot'
            )
        ]
        indexes = [
            models.Index(fields=['date', 'hour']),
            models.Index(fields=['status']),
            models.Index(fields=['user', 'date']),
        ]
