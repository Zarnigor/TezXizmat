from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class StaffTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        refresh = RefreshToken.for_user(user)

        # refresh claims
        refresh["user_type"] = "user"
        refresh["user_id"] = user.id
        refresh["email"] = user.email

        access = refresh.access_token

        # access claims
        access["user_type"] = "user"
        access["user_id"] = user.id
        access["email"] = user.email

        return {
            "refresh_token": str(refresh),
            "access_token": str(access),
        }

