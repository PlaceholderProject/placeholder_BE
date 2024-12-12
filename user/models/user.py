from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from placeholder.models.base import BaseModel

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, nickname=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        if not nickname:
            raise ValueError('닉네임은 필수입니다.')
        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, nickname=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not nickname:
            raise ValueError('슈퍼유저는 닉네임이 필요합니다.')

        return self.create_user(email, password, nickname, **extra_fields)


class User(AbstractBaseUser, BaseModel, PermissionsMixin):
    email = models.EmailField(verbose_name="이메일", max_length=64, unique=True)
    nickname = models.CharField(verbose_name="별명", max_length=8, unique=True)
    image = models.ImageField(verbose_name="프로필 이미지", upload_to="profile_images", null=True, blank=True)
    bio = models.CharField(verbose_name="자기소개", max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.email
