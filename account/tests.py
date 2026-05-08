from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from .models import AccountProfile, LoginOTPChallenge


User = get_user_model()


class LoginOTPFlowTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username="alice",
            password=self.password,
        )
        AccountProfile.objects.create(
            user=self.user,
            phone_number="+923001234567",
            phone_verified=True,
        )

    def test_password_step_creates_otp_challenge(self):
        response = self.client.post(
            reverse("password-login"),
            {"username": "alice", "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("challenge_id", response.data)
        self.assertTrue(LoginOTPChallenge.objects.filter(pk=response.data["challenge_id"]).exists())

    def test_otp_step_logs_user_in(self):
        with patch("account.views.generate_otp", return_value="123456"), patch("account.views.send_login_otp"):
            password_response = self.client.post(
                reverse("password-login"),
                {"username": "alice", "password": self.password},
                format="json",
            )
        challenge = LoginOTPChallenge.objects.get(pk=password_response.data["challenge_id"])

        response = self.client.post(
            reverse("verify-login-otp"),
            {"challenge_id": challenge.id, "otp": "123456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "alice")
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.id)
