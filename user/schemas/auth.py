import re

from pydantic import field_validator
from user.models.user import User
from placeholder.schemas.base import BaseSchema


class TokenSchema(BaseSchema):
    access: str
    refresh: str


class LoginSchema(BaseSchema):
    email: str
    password: str


class AccessSchema(BaseSchema):
    access: str


class RefreshSchema(BaseSchema):
    refresh: str


class PasswordCheckSchema(BaseSchema):
    password: str


class EmailCheckSchema(BaseSchema):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, value):
            raise ValueError("유효하지 않은 이메일 형식입니다.")
        if User.objects.filter(email=value).exists():
            raise ValueError("이미 가입된 이메일 입니다. 다른 이메일을 사용해주세요.")
        return value


class NicknameCheckSchema(BaseSchema):
    nickname: str

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value):
        if " " in value:
            raise ValueError("닉네임에는 공백이 포함될 수 없습니다.")
        if len(value) < 2 or len(value) > 8:
            raise ValueError("닉네임은 2자 이상 8자 이하이어야 합니다.")
        if User.objects.filter(nickname=value).exists():
            raise ValueError("사용 중인 닉네임 입니다. 다른 닉네임을 사용해 주세요.")
        return value


class PasswordResetSchema(PasswordCheckSchema):
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("비밀번호에 최소 1개의 특수문자가 포함되어야 합니다.")
        if not re.search(r"\d", value):
            raise ValueError("비밀번호에 최소 1개의 숫자가 포함되어야 합니다.")
        return value