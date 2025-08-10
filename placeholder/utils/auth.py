# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from ninja.security import HttpBearer
from rest_framework_simplejwt.authentication import JWTAuthentication

from placeholder.utils.exceptions import (
    InvalidTokenException,
    UnauthorizedAccessException,
)


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        jwt_auth = JWTAuthentication()
        try:
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            return user
        except Exception:
            raise InvalidTokenException()

    def get_token(self, request):
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            return auth[7:]  # Remove "Bearer " prefix
        raise UnauthorizedAccessException()


def anonymous_user(request):
    return AnonymousUser()
