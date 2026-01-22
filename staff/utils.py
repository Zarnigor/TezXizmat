# staff/utils.py
from rest_framework_simplejwt.tokens import RefreshToken

def create_staff_tokens(staff):
    """
    Staff uchun JWT:
      - role = "staff"
      - staff_id = <id>

    Eslatma: access token bilan endpointlarga kirasiz,
    shuning uchun role va staff_id access token ichida ham bo‘lishi shart.
    """
    refresh = RefreshToken()

    # Refresh token claimlari
    refresh["role"] = "staff"
    refresh["staff_id"] = staff.id

    # Access token claimlari (MUHIM)
    access = refresh.access_token
    access["role"] = "staff"
    access["staff_id"] = staff.id

    return {
        "refresh": str(refresh),
        "access": str(access),
    }
