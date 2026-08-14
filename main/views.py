from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Booking
from .permissions import (
    CanDeleteBooking,
    IsAdminOrManager,
    IsOwnerOrAdmin,
)
from .serializers import (
    AdminUserUpdateSerializer,
    BookingAdminSerializer,
    BookingSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


User = get_user_model()


def is_admin(user):
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_staff
            or user.is_superuser
        )
    )


def is_admin_or_manager(user):
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_staff
            or user.is_superuser
            or getattr(user, "is_manager", False)
        )
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("username")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]

    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
    ]

    def get_queryset(self):
        return User.objects.all().order_by("username")

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer

        if self.action in [
            "update",
            "partial_update",
        ]:
            if is_admin(self.request.user):
                return AdminUserUpdateSerializer

            return UserUpdateSerializer

        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]

        if self.action in [
            "list",
            "destroy",
        ]:
            if is_admin(self.request.user):
                return [IsAuthenticated()]
            return [IsOwnerOrAdmin()]

        if self.action in [
            "update",
            "partial_update",
            "retrieve",
        ]:
            return [IsOwnerOrAdmin()]

        if self.action in [
            "me",
            "update_profile",
        ]:
            return [IsAuthenticated()]

        return [IsAuthenticated()]

    @action(
        detail=False,
        methods=["get"],
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["put", "patch"],
    )
    def update_profile(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().select_related(
        "user",
        "confirmed_by",
    )

    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]

    ordering_fields = [
        "date",
        "hour",
        "table_number",
        "created_at",
    ]

    ordering = [
        "-date",
        "hour",
        "table_number",
    ]

    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
    ]

    def get_serializer_class(self):
        if is_admin_or_manager(self.request.user):
            return BookingAdminSerializer

        return BookingSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]

        if self.action == "destroy":
            return [CanDeleteBooking()]

        if self.action in [
            "confirm",
            "reject",
        ]:
            return [IsAdminOrManager()]

        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Booking.objects.all().select_related(
            "user",
            "confirmed_by",
        )

        date = self.request.query_params.get("date")
        if date:
            queryset = queryset.filter(date=date)

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(
                status=status_param
            )

        return queryset

    def perform_create(self, serializer):
        if is_admin_or_manager(self.request.user):
            serializer.save(
                user=self.request.user,
                status=Booking.STATUS_CONFIRMED,
                confirmed_by=self.request.user,
            )
        else:
            serializer.save(
                user=self.request.user,
                status=Booking.STATUS_PENDING,
            )

    @action(
        detail=True,
        methods=["post"],
    )
    def confirm(self, request, pk=None):
        booking = self.get_object()

        if booking.status != Booking.STATUS_PENDING:
            return Response(
                {
                    "detail":
                    'Можно подтвердить только брони '
                    'со статусом "Ожидает"'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = Booking.STATUS_CONFIRMED
        booking.confirmed_by = request.user
        booking.save()

        serializer = BookingAdminSerializer(
            booking,
            context={"request": request},
        )

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
    )
    def reject(self, request, pk=None):
        booking = self.get_object()
        booking_id = booking.id

        booking.delete()

        return Response(
            {
                "detail":
                f"Бронь #{booking_id} отклонена и удалена"
            }
        )

    @action(
        detail=False,
        methods=["get"],
    )
    def my_bookings(self, request):
        queryset = (
            Booking.objects
            .filter(user=request.user)
            .select_related(
                "user",
                "confirmed_by",
            )
            .order_by(
                "-date",
                "-hour",
            )
        )

        serializer = BookingSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
    )
    def available_slots(self, request):
        date = request.query_params.get("date")

        if not date:
            return Response(
                {"detail": "Требуется параметр date"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tables_count = getattr(
            settings,
            "TABLES_COUNT",
            5,
        )
        work_start = getattr(
            settings,
            "WORK_START",
            8,
        )
        work_end = getattr(
            settings,
            "WORK_END",
            23,
        )

        all_slots = [
            {
                "date": date,
                "hour": hour,
                "table_number": table,
            }
            for hour in range(
                work_start,
                work_end,
            )
            for table in range(
                1,
                tables_count + 1,
            )
        ]

        booked = Booking.objects.filter(
            date=date,
            status__in=[
                Booking.STATUS_PENDING,
                Booking.STATUS_CONFIRMED,
            ],
        ).values_list(
            "hour",
            "table_number",
        )

        booked_set = set(booked)

        return Response(
            [
                slot
                for slot in all_slots
                if (
                    slot["hour"],
                    slot["table_number"],
                )
                not in booked_set
            ]
        )
