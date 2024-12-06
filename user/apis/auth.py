import re

from ninja import Router, Schema, File, UploadedFile
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from ninja.security import HttpBearer
from pydantic import Field, field_validator
from typing import Optional
from django.core.files.storage import default_storage
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
    password: str = Field(..., min_length=6, max_length=15)
    nickname: str = Field(..., min_length=2, max_length=8)
    bio: Optional[str] = Field(None, max_length=40)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, value):
            raise ValueError("유효하지 않은 이메일 형식입니다.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("비밀번호에 최소 1개의 특수문자가 포함되어야 합니다.")
        if not re.search(r"\d", value):
            raise ValueError("비밀번호에 최소 1개의 숫자가 포함되어야 합니다.")
        return value

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value):
        if " " in value:
            raise ValueError("닉네임에는 공백이 포함될 수 없습니다.")
        if len(value) < 2 or len(value) > 8:
            raise ValueError("닉네임은 2자 이상 8자 이하이어야 합니다.")
        return value


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


class ProfileUpdateSchema(Schema):
    nickname: Optional[str] = Field(None, min_length=2, max_length=8, description="2자 이상 8자 이하")
    bio: Optional[str] = Field(None, max_length=40, description="최대 40자")


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


@auth_router.put("/profile", auth=JWTAuth())
@handle_exceptions
def update_profile(request, payload: ProfileUpdateSchema, image: UploadedFile = File(None)):
    if not request.auth:
        raise UnauthorizedAccessException()

    user = request.auth

    if payload.nickname:
        user.nickname = payload.nickname
    if payload.bio:
        user.bio = payload.bio

    if image:
        if user.image:
            user.image.delete()

        file_path = default_storage.save(f"profile_images/{image.name}", image)
        user.image = file_path

    user.save()
    return {
        'message': 'Profile updated successfully',
        'email': user.email,
        'nickname': user.nickname,
        'bio': user.bio,
        'image_url': user.image.url if user.image else None,
    }
