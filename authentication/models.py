from typing import Optional
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone
from shared.django import TimeStampMixin
from config.constants import DEFAULT_ROLES


class CustomUserManager(UserManager):
    """Custom user manager"""

    def create_user(self, email, username=None, password=None, **kwargs):
        if email is None:
            raise ValueError("Email field is required.")
        if password is None:
            raise ValueError("Password field is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email: str, username: Optional[str] = None, password: Optional[str] = None, **kwargs):
        _payload = kwargs
        superuser_payload = {
            "is_superuser": True,
            "is_active": True,
            "is_staff": True,
            "role_id": DEFAULT_ROLES["admin"],
        }
        _payload.update(superuser_payload)
        return self.create_user(email, username, password, **_payload)


class Role(TimeStampMixin):
    """User's Role, which is used for giving permissions"""

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin, TimeStampMixin):
    """Custom User model"""

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    age = models.PositiveSmallIntegerField(null=True, default=2)
    phone = models.CharField(max_length=13, unique=True)

    # Balance
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    role = models.ForeignKey(
        Role,
        null=True,
        default=DEFAULT_ROLES["user"],
        on_delete=models.SET_NULL,
        related_name="users",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    date_joined = models.DateTimeField(("date joined"), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = EMAIL_FIELD
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name
