from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_email_otp(to_email, otp):
    subject = "Platforma kodi"

    # Oddiy matn (fallback)
    text_content = f"Sizning tasdiqlash kodingiz: {otp}"

    # HTML dizayn
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; padding: 30px;">
        <div style="max-width: 500px; margin: auto; background: white; border-radius: 10px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center;">
          <h2 style="color: #333; font-size: 26px;">Sizning tasdiqlash kodingiz</h2>
          <p style="font-size: 32px; font-weight: bold; color: #007bff; margin-top: 20px; letter-spacing: 3px;">{otp}</p>
        </div>
      </body>
    </html>
    """

    email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()
