# -*- coding: utf-8 -*-
from typing import List

from ninja import Schema
from pydantic.alias_generators import to_camel


class BaseSchema(Schema):
    class Config(Schema.Config):
        alias_generator = to_camel
        populate_by_name = True

    def model_dump(self, **kwargs):
        return super().model_dump(by_alias=kwargs.get("by_alias", True))

    def dict(self, **kwargs):
        return super().model_dump(by_alias=kwargs.get("by_alias", True))


class ResultSchema(BaseSchema):
    result: List


class ErrorSchema(BaseSchema):
    message: str


class PresignedUrlSchema(BaseSchema):
    result: List
