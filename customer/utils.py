import random
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email, otp):
    send_mail(
        "OTP Code",
        f"Your OTP: {otp}",
        None,
        [email]
    )

def send_email(email: str, code: str):
    subject = "🔐 TezXizmat – Tasdiqlash kodi"

    # Plain text (fallback)
    text_content = f"""
Salom!

Sizning tasdiqlash kodingiz: {code}

Kod 1 daqiqa amal qiladi.
Agar bu siz bo‘lmasangiz, xabarni e'tiborsiz qoldiring.

TezXizmat jamoasi
"""

    # HTML content
    html_content = render_to_string(
        "emails/otp_email.html",
        {
            "code": code,
        }
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()
