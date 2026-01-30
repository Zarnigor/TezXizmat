from rest_framework_simplejwt.tokens import RefreshToken

def create_staff_tokens(staff):
    refresh = RefreshToken.for_user(staff)

    refresh["role"] = "staff"
    refresh["staff_id"] = staff.id

    return {
        "id": staff.id,
        "first_name": staff.first_name,
        "last_name": staff.last_name,
        "email": staff.email,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
