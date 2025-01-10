# -*- coding: utf-8 -*-
from ninja import File, Form, Router
from ninja.files import UploadedFile

from placeholder.utils.auth import JWTAuth
from placeholder.utils.decorators import handle_exceptions
from user.models.user import User
from user.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema

user_router = Router(tags=["User"])


@user_router.post("", response={201: None})
@handle_exceptions
def create_user(request, payload: UserCreateSchema):
    User.objects.create_user(**payload.dict())
    return 201, None


@user_router.get("/me", response={200: UserSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def get_user(request):
    user = request.auth
    return 200, user


@user_router.put("/me", response={200: UserSchema}, auth=JWTAuth(), by_alias=True)
@handle_exceptions
def update_user(request, item: Form[UserUpdateSchema], image: UploadedFile = File(None)):
    user = request.auth

    for attr, value in item.model_dump(by_alias=False).items():
        setattr(user, attr, value)

    if image:
        user.image = image
    user.save()

    return 200, user


@user_router.delete("/me", response={204: None}, auth=JWTAuth())
@handle_exceptions
def delete_user(request):
    user = request.auth

    user.delete()
    return 204, None
