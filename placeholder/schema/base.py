from pydantic.alias_generators import to_camel
from ninja import Schema


class BaseSchema(Schema):
    class Config(Schema.Config):
        alias_generator = to_camel

    def model_dump(self, **kwargs):
        return super().model_dump(by_alias=kwargs.get("by_alias", True))

    def dict(self, **kwargs):
        return super().model_dump(by_alias=kwargs.get("by_alias", True))


class Error(Schema):
    message: str
