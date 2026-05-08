from django.conf import settings
from django.contrib.auth import login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LoginOTPChallenge
from .serializers import OTPVerifySerializer, PasswordLoginSerializer
from .services import generate_otp, hash_otp, send_login_otp, verify_otp


class PasswordLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = PasswordLoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        phone_number = serializer.validated_data["phone_number"]
        otp = generate_otp()

        challenge = LoginOTPChallenge.objects.create(
            user=user,
            phone_number=phone_number,
            code_hash=hash_otp(otp),
            expires_at=LoginOTPChallenge.expiry_time(),
        )
        send_login_otp(phone_number=phone_number, code=otp)

        data = {
            "detail": "Password verified. OTP sent to the registered phone number.",
            "challenge_id": challenge.id,
            "expires_at": challenge.expires_at,
        }
        if settings.DEBUG:
            data["debug_otp"] = otp

        return Response(data, status=status.HTTP_200_OK)


class VerifyLoginOTPView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        challenge = serializer.validated_data["challenge_id"]
        otp = serializer.validated_data["otp"]

        if challenge.is_used:
            return Response({"detail": "This OTP has already been used."}, status=status.HTTP_400_BAD_REQUEST)
        if challenge.is_expired():
            return Response({"detail": "This OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
        if not challenge.has_attempts_remaining():
            return Response({"detail": "Maximum OTP attempts exceeded."}, status=status.HTTP_400_BAD_REQUEST)
        if not verify_otp(otp, challenge.code_hash):
            challenge.attempts += 1
            challenge.save(update_fields=["attempts"])
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        challenge.is_used = True
        challenge.save(update_fields=["is_used"])
        login(request, challenge.user)

        return Response(
            {
                "detail": "Login successful.",
                "user_id": challenge.user_id,
                "username": challenge.user.get_username(),
            },
            status=status.HTTP_200_OK,
        )
