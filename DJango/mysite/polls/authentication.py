# your_app/authentication.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result
        if token["jti"] != getattr(user, "current_token_jti", None):
            raise AuthenticationFailed("Token has been revoked")
        return (user, token)
