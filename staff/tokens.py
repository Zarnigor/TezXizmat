from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class StaffTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)  # bu RefreshToken

        # refresh claims
        token["user_type"] = "staff"
        token["user_id"] = user.id
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)  # default: {"refresh": "...", "access": "..."}

        # xohlasangiz key nomlarini o'zgartirib berasiz:
        data["refresh_token"] = data.pop("refresh")
        data["access_token"] = data.pop("access")

        return data
