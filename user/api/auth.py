from ninja import Router
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
)
from user.schema.auth import LoginSchema, RefreshSchema, PasswordCheckSchema, TokenSchema, EmailCheckSchema, NicknameCheckSchema, AccessSchema
from placeholder.utils.auth import JWTAuth
from placeholder.schema.base import Error

auth_router = Router()


@auth_router.post("/email", response={200: None})
@handle_exceptions
def check_email(request, payload: EmailCheckSchema):
    return 200, None


@auth_router.post("/nickname", response={200: None})
@handle_exceptions
def check_nickname(request, payload: NicknameCheckSchema):
    return 200, None


@auth_router.post("/login", response={200: TokenSchema})
@handle_exceptions
def login(request, payload: LoginSchema):
    user = authenticate(email=payload.email, password=payload.password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return 200, {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    else:
        raise InvalidCredentialsException()


@auth_router.post("/refresh", auth=JWTAuth(), response={200: AccessSchema})
@handle_exceptions
def refresh_token(request, payload: RefreshSchema):
    try:
        refresh = RefreshToken(payload.refresh)
        return 200, {'access': str(refresh.access_token)}
    except Exception:
        raise InvalidTokenException()


@auth_router.post("/password", auth=JWTAuth(), response={200: None, 400: Error})
@handle_exceptions
def check_password(request, payload: PasswordCheckSchema):
    user = request.auth

    if user.check_password(payload.password):
        return 200, None
    return 400, {"message": "비밀번호가 맞지 않습니다"}
