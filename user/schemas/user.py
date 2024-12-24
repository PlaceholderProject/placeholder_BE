from pydantic import Field, field_validator
import re
from user.models.user import User
from placeholder.schemas.base import BaseSchema
from ninja.orm import create_schema


class UserCreateSchema(BaseSchema):
    email: str
    password: str = Field(..., min_length=6, max_length=15)
    nickname: str = Field(..., min_length=2, max_length=8)
    bio: str | None = Field(None, max_length=40)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, value):
            raise ValueError("유효하지 않은 이메일 형식입니다.")

        if User.objects.filter(email=value).exists() is True:
            raise ValueError("이미 가입된 이메일 입니다. 다른 이메일을 사용해주세요.")
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
        if User.objects.filter(nickname=value).exists() is True:
            raise ValueError("사용 중인 닉네임 입니다. 다른 닉네임을 사용해 주세요.")
        return value


class UserUpdateSchema(BaseSchema):
    nickname: str = Field(..., min_length=2, max_length=8, description="2자 이상 8자 이하")
    bio: str = Field(..., max_length=40, description="최대 40자")

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value):
        if " " in value:
            raise ValueError("닉네임에는 공백이 포함될 수 없습니다.")
        if len(value) < 2 or len(value) > 8:
            raise ValueError("닉네임은 2자 이상 8자 이하이어야 합니다.")
        if User.objects.filter(nickname=value).exists() is True:
            raise ValueError("사용 중인 닉네임 입니다. 다른 닉네임을 사용해 주세요.")
        return value


UserSchema = create_schema(User, fields=["email", "nickname", "bio", "image"])
