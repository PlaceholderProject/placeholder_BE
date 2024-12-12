from ninja import Router, Schema
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
)
from user.schema.auth import LoginSchema, RefreshSchema, PasswordCheckSchema
from placeholder.utils.auth import JWTAuth

auth_router = Router()


class Error(Schema):
    message: str


class TokenSchema(Schema):
    access: str
    refresh: str


@auth_router.post("/email", auth=JWTAuth())
@handle_exceptions
def check_email(request, payload: PasswordCheckSchema):
    return 200


@auth_router.post("/nickname", auth=JWTAuth())
@handle_exceptions
def check_nickname(request, payload: PasswordCheckSchema):
    return 200


@auth_router.post("/login")
@handle_exceptions
def login(request, payload: LoginSchema):
    user = authenticate(email=payload.email, password=payload.password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    else:
        raise InvalidCredentialsException()


@auth_router.post("/refresh")
@handle_exceptions
def refresh_token(request, payload: RefreshSchema):
    try:
        refresh = RefreshToken(payload.refresh)
        data = {'access': str(refresh.access_token)}
        return data
    except Exception:
        raise InvalidTokenException()


@auth_router.post("/password", auth=JWTAuth())
@handle_exceptions
def check_password(request, payload: PasswordCheckSchema):
    user = request.auth

    if user.check_password(payload.password):
        return 200
    return 400
