from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from .base import TimeStampedModel, PhoneNumberModel


class UserManager(BaseUserManager):
    """Custom manager for User model."""

    def create_user(self, email, username, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        if not username:
            raise ValueError("Username is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def suggest_usernames(self, name_base):
        """Suggest unique usernames based on name or random fallback."""
        base = name_base.replace(" ", "").lower()
        suggestions = []
        for _ in range(3):
            suffix = get_random_string(4).lower()
            suggestion = f"{base}{suffix}"
            if not self.model.objects.filter(username=suggestion).exists():
                suggestions.append(suggestion)
        return suggestions

    def is_username_available(self, username):
        return not self.model.objects.filter(username=username).exists()


class User(AbstractBaseUser, TimeStampedModel, PhoneNumberModel):
    """Custom user model with clean separation of logic and attributes."""
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']

    objects = UserManager()

    def __str__(self):
        return self.username

    def update_profile(self, name=None, phone=None):
        self.name = name or self.name
        self.phone = phone or self.phone
        self.save()

    def change_password(self, current_password, new_password):
        if not self.check_password(current_password):
            return False, "Current password is incorrect."
        self.set_password(new_password)
        self.save()
        return True, None
