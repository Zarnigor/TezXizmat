import random

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.template.loader import render_to_string


def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email, otp):
    send_mail(
        "OTP Code",
        f"Your OTP: {otp}",
        None,
        [email]
    )

