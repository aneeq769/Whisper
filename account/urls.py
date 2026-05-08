from django.urls import path

from .views import PasswordLoginView, VerifyLoginOTPView


urlpatterns = [
    path("login/password/", PasswordLoginView.as_view(), name="password-login"),
    path("login/verify-otp/", VerifyLoginOTPView.as_view(), name="verify-login-otp"),
]
