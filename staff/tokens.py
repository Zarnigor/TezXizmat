# staff/tokens.py
from rest_framework_simplejwt.tokens import RefreshToken

def create_staff_tokens(staff):
    # RefreshToken() userga bog'liq emas, manual claim qo'yamiz
    refresh = RefreshToken()
    refresh["role"] = "staff"
    refresh["staff_id"] = staff.id
    refresh["email"] = staff.email

    access = refresh.access_token
    access["role"] = "staff"
    access["staff_id"] = staff.id
    access["email"] = staff.email

    return {"refresh": str(refresh), "access": str(access)}
