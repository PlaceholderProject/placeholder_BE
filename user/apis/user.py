from ninja import Router, File
from django.core.files.storage import default_storage
from placeholder.utils.decorators import handle_exceptions
from user.schemas.user import UserCreateSchema, UserUpdateSchema, UserSchema
from placeholder.utils.auth import JWTAuth
from ninja.files import UploadedFile
from user.models.user import User


user_router = Router(tags=["User"])


@user_router.post("", response={201: None})
@handle_exceptions
def create_user(request, payload: UserCreateSchema):
    User.objects.create_user(**payload.dict())
    return 201, None


@user_router.get("", auth=JWTAuth(), response={200: UserSchema})
@handle_exceptions
def get_user(request):
    user = request.auth

    return 200, {
        'email': user.email,
        'nickname': user.nickname,
        'bio': user.bio,
        'image_url': user.image.url if user.image else "",
    }


@user_router.put("", auth=JWTAuth())
@handle_exceptions
def update_user(request, payload: UserUpdateSchema, image: UploadedFile = File(None)):
    user = request.auth

    user.nickname = payload.nickname
    user.bio = payload.bio

    if image:
        file_path = default_storage.save(f"profile_images/{image.name}", image)
        user.image = file_path
    user.save()

    return 200, {
        'email': user.email,
        'nickname': user.nickname,
        'bio': user.bio,
        'image_url': user.image.url if user.image else "",
    }


@user_router.delete("", auth=JWTAuth(), response={204: None})
@handle_exceptions
def delete_user(request):
    user = request.auth

    user.delete()
    return 204, None
