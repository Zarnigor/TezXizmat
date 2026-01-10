# customer/utils.py
import random
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email, otp):
    send_mail(
        "OTP Code",
        f"Your OTP: {otp}",
        None,
        [email]
    )
