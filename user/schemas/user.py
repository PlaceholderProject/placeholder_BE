# -*- coding: utf-8 -*-
import re
from datetime import datetime
from typing import List

from ninja.orm import create_schema
from pydantic import Field, field_validator

from placeholder.schemas.base import BaseSchema
from user.models.user import User


class UserCreateSchema(BaseSchema):
    email: str
    password: str = Field(..., min_length=6, max_length=15)
    nickname: str = Field(..., min_length=2, max_length=8)
    bio: str | None = Field(None, max_length=40)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
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


UserSchema = create_schema(User, fields=["email", "nickname", "bio", "image"], base_class=BaseSchema)

UserUpdateSchema = create_schema(User, fields=["nickname", "bio"], base_class=BaseSchema)

UserProfileSchema = create_schema(User, fields=["nickname", "image"], base_class=BaseSchema)


class MyMeetupSchema(BaseSchema):
    id: int
    is_organizer: bool
    name: str
    ended_at: datetime
    is_current: bool


class MyAdSchema(BaseSchema):
    id: int
    ad_title: str
    ad_ended_at: datetime
    is_current: bool


class MyMeetupListSchema(BaseSchema):
    result: List[MyMeetupSchema]


class MyAdListSchema(BaseSchema):
    result: List[MyAdSchema]


class MyProposalSchema(BaseSchema):
    id: int
    meetup_name: str
    text: str
    status: str
    created_at: datetime


class MyProposalListSchema(BaseSchema):
    result: List[MyProposalSchema]
