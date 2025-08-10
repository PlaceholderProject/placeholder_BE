# -*- coding: utf-8 -*-
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestUserModel:
    """User 모델 테스트"""

    def test_create_user_success(self):
        """사용자 생성 성공 테스트"""
        user = User.objects.create_user(email="test@example.com", password="Test123!", nickname="테스터")

        assert user.email == "test@example.com"
        assert user.nickname == "테스터"
        assert user.check_password("Test123!")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_with_bio(self):
        """bio와 함께 사용자 생성 테스트"""
        bio = "테스트 사용자입니다"
        user = User.objects.create_user(email="test@example.com", password="Test123!", nickname="테스터", bio=bio)

        assert user.bio == bio

    def test_create_user_without_email_fails(self):
        """이메일 없이 사용자 생성 실패 테스트"""
        with pytest.raises(ValueError, match="이메일은 필수입니다."):
            User.objects.create_user(email="", password="Test123!", nickname="테스터")

    def test_create_user_without_nickname_fails(self):
        """닉네임 없이 사용자 생성 실패 테스트"""
        with pytest.raises(ValueError, match="닉네임은 필수입니다."):
            User.objects.create_user(email="test@example.com", password="Test123!", nickname="")

    def test_create_superuser_success(self):
        """슈퍼유저 생성 성공 테스트"""
        user = User.objects.create_superuser(email="admin@example.com", password="Admin123!", nickname="관리자")

        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.nickname == "관리자"

    def test_create_superuser_without_nickname_fails(self):
        """닉네임 없이 슈퍼유저 생성 실패 테스트"""
        with pytest.raises(ValueError, match="슈퍼유저는 닉네임이 필요합니다."):
            User.objects.create_superuser(email="admin@example.com", password="Admin123!", nickname="")

    def test_email_normalization(self):
        """이메일 정규화 테스트"""
        user = User.objects.create_user(email="Test@EXAMPLE.COM", password="Test123!", nickname="테스터")

        assert user.email == "Test@example.com"

    def test_unique_email_constraint(self):
        """이메일 유니크 제약 테스트"""
        User.objects.create_user(email="test@example.com", password="Test123!", nickname="테스터1")

        with pytest.raises(IntegrityError):
            User.objects.create_user(email="test@example.com", password="Test123!", nickname="테스터2")

    def test_unique_nickname_constraint(self):
        """닉네임 유니크 제약 테스트"""
        User.objects.create_user(email="test1@example.com", password="Test123!", nickname="테스터")

        with pytest.raises(IntegrityError):
            User.objects.create_user(email="test2@example.com", password="Test123!", nickname="테스터")

    def test_user_str_representation(self):
        """User __str__ 메서드 테스트"""
        user = User.objects.create_user(email="test@example.com", password="Test123!", nickname="테스터")

        assert str(user) == "test@example.com"

    def test_user_fields_max_length(self):
        """User 필드 최대 길이 테스트"""
        # 닉네임 최대 8자
        user = User.objects.create_user(email="test@example.com", password="Test123!", nickname="12345678")  # 8자
        assert len(user.nickname) == 8

        # bio 최대 40자
        long_bio = "a" * 40
        user.bio = long_bio
        user.save()
        assert len(user.bio) == 40
