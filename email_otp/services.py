from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError

from .models import EmailOTP
from .utils import generate_otp

OTP_EXPIRE_SECONDS = 50
VERIFIED_GRACE_SECONDS = 10 * 60  # 10 min


def norm_email(email: str) -> str:
    return (email or "").strip().lower()


def user_exists_in_any(email: str) -> bool:
    """Email global unique: Customer yoki Staffda bo‘lsa band."""
    email = norm_email(email)

    try:
        from customer.models import Customer  # type: ignore
        if Customer.objects.filter(email=email).exists():
            return True
    except Exception:
        pass

    try:
        from staff.models import Staff  # type: ignore
        if Staff.objects.filter(email=email).exists():
            return True
    except Exception:
        pass

    return False


def get_actor_user(email: str, actor: str):
    email = norm_email(email)
    if actor == EmailOTP.ACTOR_CUSTOMER:
        try:
            from customer.models import Customer  # type: ignore
            return Customer.objects.filter(email=email).first()
        except Exception:
            return None

    if actor == EmailOTP.ACTOR_STAFF:
        try:
            from staff.models import Staff  # type: ignore
            return Staff.objects.filter(email=email).first()
        except Exception:
            return None

    return None


def _send_email(email: str, code: str):
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


def send_otp(*, email: str, purpose: str, actor: str) -> EmailOTP:
    email = norm_email(email)

    if purpose not in (EmailOTP.PURPOSE_VERIFY, EmailOTP.PURPOSE_RESET):
        raise ValidationError({"purpose": "Noto‘g‘ri purpose"})

    if actor not in (EmailOTP.ACTOR_CUSTOMER, EmailOTP.ACTOR_STAFF):
        raise ValidationError({"actor": "Noto‘g‘ri actor"})

    if purpose == EmailOTP.PURPOSE_VERIFY:
        # registerdan oldin: email hech qayerda band bo‘lmasligi kerak
        if user_exists_in_any(email):
            raise ValidationError({"email": "Bu email allaqachon band (customer yoki staffda mavjud)."})
    else:
        # RESET: actor user bo‘lishi shart va email verified bo‘lishi shart
        user = get_actor_user(email, actor)
        if not user:
            raise ValidationError({"email": "Bu email bilan foydalanuvchi topilmadi."})
        if hasattr(user, "is_email_verified") and not user.is_email_verified:
            raise ValidationError({"email": "Email tasdiqlanmagan. RESET uchun avval VERIFY bo‘lishi kerak."})

    code = generate_otp()
    expires_at = timezone.now() + timedelta(seconds=OTP_EXPIRE_SECONDS)

    otp, _ = EmailOTP.objects.update_or_create(
        email=email,
        purpose=purpose,
        actor=actor,
        defaults={
            "code": code,
            "expires_at": expires_at,
            "state": EmailOTP.STATE_SENT,
            "verified_at": None,
        },
    )

    _send_email(email, code)
    return otp


def verify_otp(*, email: str, code: str, purpose: str, actor: str) -> None:
    email = norm_email(email)
    code = (code or "").strip()

    otp = (
        EmailOTP.objects
        .filter(email=email, purpose=purpose, actor=actor)
        .order_by("-created_at")
        .first()
    )
    if not otp:
        raise ValidationError({"detail": "OTP topilmadi."})

    if otp.is_expired():
        raise ValidationError({"detail": "OTP muddati o‘tgan."})

    if otp.code != code:
        raise ValidationError({"code": "Kod xato."})

    otp.state = EmailOTP.STATE_VERIFIED
    otp.verified_at = timezone.now()
    otp.save(update_fields=["state", "verified_at", "updated_at"])


def is_email_verified(*, email: str, purpose: str, actor: str) -> bool:
    """
    Customer/Staff register/reset uchun:
    VERIFIED bo‘lganidan keyin VERIFIED_GRACE_SECONDS ichida true.
    """
    email = norm_email(email)
    now = timezone.now()

    otp = (
        EmailOTP.objects
        .filter(
            email=email,
            purpose=purpose,
            actor=actor,
            state=EmailOTP.STATE_VERIFIED,
        )
        .order_by("-verified_at")
        .first()
    )

    if not otp or not otp.verified_at:
        return False

    return now <= (otp.verified_at + timedelta(seconds=VERIFIED_GRACE_SECONDS))
