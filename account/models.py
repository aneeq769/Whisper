from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


User = get_user_model()


class AccountProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_profile",
    )
    phone_number = models.CharField(max_length=20, unique=True)
    phone_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} profile"


class LoginOTPChallenge(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="login_otp_challenges",
    )
    phone_number = models.CharField(max_length=20)
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def expiry_time(cls):
        minutes = getattr(settings, "ACCOUNT_OTP_EXPIRY_MINUTES", 5)
        return timezone.now() + timedelta(minutes=minutes)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def has_attempts_remaining(self):
        return self.attempts < self.max_attempts
