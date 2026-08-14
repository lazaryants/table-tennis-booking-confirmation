# /var/www/ttennis/main/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BookingViewSet  # 🔥 Убрали BookingAdminViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
]
