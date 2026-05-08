import importlib
import logging
import secrets

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password


logger = logging.getLogger(__name__)


def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(code):
    return make_password(code)


def verify_otp(code, code_hash):
    return check_password(code, code_hash)


def send_login_otp(phone_number, code):
    backend_path = getattr(settings, "ACCOUNT_SMS_BACKEND", "")
    if backend_path:
        module_path, function_name = backend_path.rsplit(".", 1)
        sender = getattr(importlib.import_module(module_path), function_name)
        sender(phone_number=phone_number, message=f"Your login OTP is {code}")
        return

    logger.info("OTP for %s is %s", phone_number, code)
