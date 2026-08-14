from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Booking


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Полный профиль пользователя.
    Используется для собственного профиля и администратором.
    """

    bookings_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "is_manager",
            "is_staff",
            "is_active",
            "date_joined",
            "last_login",
            "bookings_count",
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "last_login",
            "bookings_count",
        ]

    def get_bookings_count(self, obj):
        return obj.bookings.count()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Публичная регистрация.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Изменение собственного профиля.
    Служебные роли здесь изменить нельзя.
    """

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
        ]
        extra_kwargs = {
            "email": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "phone": {"required": False},
        }


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Изменение пользователя администратором.
    """

    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "is_staff",
            "is_active",
            "is_manager",
            "password",
        ]
        extra_kwargs = {
            "email": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "phone": {"required": False},
            "is_staff": {"required": False},
            "is_active": {"required": False},
            "is_manager": {"required": False},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class BookingSerializer(serializers.ModelSerializer):
    """
    Представление брони для обычного пользователя.

    Намеренно НЕ содержит:
    - телефон;
    - email;
    - служебные данные подтверждающего.

    Имя оставляем, поскольку оно отображается в общей таблице клуба.
    """

    user_name = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    user_first_name = serializers.CharField(
        source="user.first_name",
        read_only=True,
    )
    user_last_name = serializers.CharField(
        source="user.last_name",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "user_name",
            "user_first_name",
            "user_last_name",
            "date",
            "hour",
            "table_number",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError(
                "Нельзя создать бронь на прошедшую дату"
            )

        return value

    def validate(self, data):
        date = data.get("date")
        hour = data.get("hour")
        table_number = data.get("table_number")

        if date and hour and table_number:
            existing = Booking.objects.filter(
                date=date,
                hour=hour,
                table_number=table_number,
                status__in=[
                    Booking.STATUS_PENDING,
                    Booking.STATUS_CONFIRMED,
                ],
            )

            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise serializers.ValidationError(
                    f"Стол {table_number} на {date} "
                    f"в {hour:02d}:00 уже забронирован"
                )

        return data

    def create(self, validated_data):
        request = self.context.get("request")

        if request:
            validated_data["user"] = request.user

        validated_data["status"] = Booking.STATUS_PENDING

        return super().create(validated_data)


class BookingAdminSerializer(serializers.ModelSerializer):
    """
    Полное представление брони для администратора или менеджера.
    """

    user_name = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    user_first_name = serializers.CharField(
        source="user.first_name",
        read_only=True,
    )
    user_last_name = serializers.CharField(
        source="user.last_name",
        read_only=True,
    )
    user_email = serializers.CharField(
        source="user.email",
        read_only=True,
    )
    user_phone = serializers.CharField(
        source="user.phone",
        read_only=True,
    )
    confirmed_by_name = serializers.CharField(
        source="confirmed_by.username",
        read_only=True,
        allow_null=True,
    )

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        date = data.get(
            "date",
            self.instance.date if self.instance else None,
        )
        hour = data.get(
            "hour",
            self.instance.hour if self.instance else None,
        )
        table_number = data.get(
            "table_number",
            self.instance.table_number if self.instance else None,
        )
        booking_status = data.get(
            "status",
            self.instance.status if self.instance else Booking.STATUS_PENDING,
        )

        if (
            date
            and hour
            and table_number
            and booking_status
            in [
                Booking.STATUS_PENDING,
                Booking.STATUS_CONFIRMED,
            ]
        ):
            existing = Booking.objects.filter(
                date=date,
                hour=hour,
                table_number=table_number,
                status__in=[
                    Booking.STATUS_PENDING,
                    Booking.STATUS_CONFIRMED,
                ],
            )

            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise serializers.ValidationError(
                    f"Стол {table_number} на {date} "
                    f"в {hour:02d}:00 уже забронирован"
                )

        return data
