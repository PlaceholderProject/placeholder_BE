from django.db import models
from placeholder.models.base import BaseModel
from placeholder.utils.enums import StrEnum


class Category(BaseModel):
    class CategoryType(StrEnum):
        CLASSIFICATION = ("CLASSIFICATION", "분류")
        REGION = ("REGION", "지역")

    name = models.CharField(max_length=255, unique=True)
    slug = models.CharField(max_length=255, unique=True)
    type = models.CharField(verbose_name="타입", choices=CategoryType.get_values, default=CategoryType.CLASSIFICATION.value)

    def __str__(self):
        return self.name
