import re
from rest_framework.exceptions import ValidationError

def validate_password(password):
    if len(password) < 8:
        raise ValidationError("Parol kamida 8 ta belgidan iborat bo‘lishi kerak")
    if not re.search(r"[A-Za-z]", password):
        raise ValidationError("Parolda harf bo‘lishi kerak")
    if not re.search(r"\d", password):
        raise ValidationError("Parolda son bo‘lishi kerak")
