from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import LoginOTPChallenge


User = get_user_model()


class PasswordLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        request = self.context.get("request")
        user = authenticate(
            request=request,
            username=attrs["username"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        try:
            profile = user.account_profile
        except User.account_profile.RelatedObjectDoesNotExist:
            raise serializers.ValidationError("No phone number is configured for this account.")
        if not profile.phone_verified:
            raise serializers.ValidationError("The phone number for this account is not verified.")

        attrs["user"] = user
        attrs["phone_number"] = profile.phone_number
        return attrs


class OTPVerifySerializer(serializers.Serializer):
    challenge_id = serializers.IntegerField()
    otp = serializers.CharField(min_length=4, max_length=6, trim_whitespace=True)

    def validate_challenge_id(self, value):
        try:
            challenge = LoginOTPChallenge.objects.select_related("user").get(pk=value)
        except LoginOTPChallenge.DoesNotExist as exc:
            raise serializers.ValidationError("Invalid OTP challenge.") from exc
        return challenge
