# -*- coding: utf-8 -*-
import json

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestAuthAPI:
    """인증 API 테스트"""

    def setup_method(self):
        """테스트 메서드 실행 전 초기화"""
        self.client = Client()
        self.register_url = "/api/v1/user"  # 실제 등록 URL
        self.login_url = "/api/v1/auth/login"
        self.refresh_url = "/api/v1/auth/refresh"
        self.email_check_url = "/api/v1/auth/email"
        self.nickname_check_url = "/api/v1/auth/nickname"

    def test_email_check_available(self):
        """사용 가능한 이메일 확인 테스트"""
        data = {"email": "available@example.com"}
        response = self.client.post(self.email_check_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 200

    def test_email_check_already_exists(self):
        """이미 존재하는 이메일 확인 테스트"""
        # 먼저 사용자 생성
        User.objects.create_user(email="existing@example.com", password="Test123!", nickname="기존사용자")

        data = {"email": "existing@example.com"}
        response = self.client.post(self.email_check_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 422  # 실제 응답 상태코드에 맞춤
        # Django-Ninja 검증 에러 응답 구조에 맞춤
        error_response = response.json()
        assert "detail" in error_response
        assert "이미 가입된 이메일" in error_response["detail"][0]["msg"]

    def test_nickname_check_available(self):
        """사용 가능한 닉네임 확인 테스트"""
        data = {"nickname": "새닉네임"}
        response = self.client.post(self.nickname_check_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 200

    def test_nickname_check_already_exists(self):
        """이미 존재하는 닉네임 확인 테스트"""
        # 먼저 사용자 생성
        User.objects.create_user(email="test@example.com", password="Test123!", nickname="기존닉네임")

        data = {"nickname": "기존닉네임"}
        response = self.client.post(self.nickname_check_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 422
        # Django-Ninja 검증 에러 응답 구조에 맞춤
        error_response = response.json()
        assert "detail" in error_response
        assert "사용 중인 닉네임" in error_response["detail"][0]["msg"]

    def test_user_registration_success(self):
        """사용자 등록 성공 테스트"""
        data = {"email": "newuser@example.com", "password": "NewUser123!", "nickname": "새사용자", "bio": "새로운 사용자입니다"}

        response = self.client.post(self.register_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 201

        # 데이터베이스에 사용자가 생성되었는지 확인
        user = User.objects.get(email=data["email"])
        assert user.nickname == data["nickname"]
        assert user.check_password(data["password"])

    def test_user_registration_invalid_email(self):
        """잘못된 이메일로 사용자 등록 실패 테스트"""
        data = {"email": "invalid-email", "password": "Test123!", "nickname": "테스터"}

        response = self.client.post(self.register_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 422

    def test_user_registration_weak_password(self):
        """약한 패스워드로 사용자 등록 실패 테스트"""
        data = {"email": "test@example.com", "password": "weak", "nickname": "테스터"}  # 특수문자, 숫자 없음

        response = self.client.post(self.register_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 422

    def test_user_registration_invalid_nickname(self):
        """잘못된 닉네임으로 사용자 등록 실패 테스트"""
        data = {"email": "test@example.com", "password": "Test123!", "nickname": "닉네임 공백"}  # 공백 포함

        response = self.client.post(self.register_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 422

    def test_user_login_success(self):
        """사용자 로그인 성공 테스트"""
        # 먼저 사용자 생성
        password = "Test123!"
        user = User.objects.create_user(email="test@example.com", password=password, nickname="테스터")

        data = {"email": "test@example.com", "password": password}

        response = self.client.post(self.login_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 200
        response_data = response.json()
        assert "access" in response_data  # 실제 필드명에 맞춤
        assert "refresh" in response_data

    def test_user_login_invalid_credentials(self):
        """잘못된 인증정보로 로그인 실패 테스트"""
        # 먼저 사용자 생성
        User.objects.create_user(email="test@example.com", password="Test123!", nickname="테스터")

        data = {"email": "test@example.com", "password": "WrongPassword!"}

        response = self.client.post(self.login_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 401
        assert "유효하지 않은 자격 증명입니다" in response.json()["detail"]

    def test_user_login_nonexistent_user(self):
        """존재하지 않는 사용자로 로그인 실패 테스트"""
        data = {"email": "nonexistent@example.com", "password": "Test123!"}

        response = self.client.post(self.login_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 401
        assert "유효하지 않은 자격 증명입니다" in response.json()["detail"]

    def test_token_refresh_success(self):
        """토큰 갱신 성공 테스트"""
        # 사용자 생성 및 토큰 발급
        user = User.objects.create_user(email="test@example.com", password="Test123!", nickname="테스터")

        refresh = RefreshToken.for_user(user)

        data = {"refresh": str(refresh)}  # 실제 필드명에 맞춤

        response = self.client.post(self.refresh_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code == 200
        response_data = response.json()
        assert "access" in response_data

    def test_token_refresh_invalid_token(self):
        """잘못된 토큰으로 갱신 실패 테스트"""
        data = {"refresh": "invalid_token"}

        response = self.client.post(self.refresh_url, data=json.dumps(data), content_type="application/json")

        assert response.status_code in [401, 422]  # 토큰 검증 실패시 다양한 상태코드 가능
