import re
from rest_framework import serializers

PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")

def validate_password_policy(password: str):
    if not PASSWORD_REGEX.match(password or ""):
        raise serializers.ValidationError(
            "Parol kamida 8 ta belgi bo‘lsin va ichida kamida 1 harf hamda 1 raqam bo‘lsin."
        )
