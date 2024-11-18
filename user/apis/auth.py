from ninja import Router, Schema, File
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from ninja.security import HttpBearer
from pydantic import Field
from typing import Optional
from django.core.files.uploadedfile import InMemoryUploadedFile

from placeholder.utils.decorators import handle_exceptions
from placeholder.utils.exceptions import (
    EmailAlreadyExistsException,
    NicknameAlreadyExistsException,
    InvalidCredentialsException,
    InvalidTokenException,
    UnauthorizedAccessException,
)

User = get_user_model()

auth_router = Router()


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
        auth = request.headers.get('Authorization')
        if not auth:
            raise UnauthorizedAccessException()
        try:
            scheme, token = auth.split()
            if scheme.lower() != 'bearer':
                raise UnauthorizedAccessException()
            return token
        except ValueError:
            raise UnauthorizedAccessException()


class RegisterSchema(Schema):
    email: str
    password: str = Field(..., min_length=8)
    nickname: str = Field(..., min_length=3, max_length=8)
    bio: Optional[str] = Field(None, max_length=40)


class LoginSchema(Schema):
    email: str
    password: str


class RefreshSchema(Schema):
    refresh: str


@auth_router.post("/register")
@handle_exceptions
def register(request, payload: RegisterSchema):
    if User.objects.filter(email=payload.email).exists():
        raise EmailAlreadyExistsException()
    if User.objects.filter(nickname=payload.nickname).exists():
        raise NicknameAlreadyExistsException()

    user = User.objects.create_user(
        email=payload.email,
        password=payload.password,
        nickname=payload.nickname,
        bio=payload.bio
    )

    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


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
def token_refresh(request, payload: RefreshSchema):
    try:
        refresh = RefreshToken(payload.refresh)
        data = {'access': str(refresh.access_token)}
        return data
    except Exception:
        raise InvalidTokenException()


@auth_router.get("/profile", auth=JWTAuth())
@handle_exceptions
def profile(request):
    if not request.auth:
        raise UnauthorizedAccessException()
    user = request.auth
    return {
        'email': user.email,
        'nickname': user.nickname,
        'bio': user.bio,
        'image_url': user.image.url if user.image else None,
    }
