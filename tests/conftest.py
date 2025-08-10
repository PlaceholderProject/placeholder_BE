# -*- coding: utf-8 -*-
import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import transaction
from django.test import Client
from rest_framework_simplejwt.tokens import RefreshToken

from meetup.models import Meetup, Member
from meetup.models.member import Member as MemberModel

User = get_user_model()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """모든 테스트에서 데이터베이스 접근 허용"""
    pass


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    """데이터베이스 설정"""
    with django_db_blocker.unblock():
        call_command("migrate", "--run-syncdb")


@pytest.fixture(autouse=True)
def clean_db_after_test(transactional_db):
    """각 테스트 후 트랜잭션 롤백으로 데이터베이스 정리"""
    yield
    # Django의 TestCase처럼 트랜잭션 롤백을 통한 정리


@pytest.fixture
def api_client():
    """Django Test Client"""
    return Client()


@pytest.fixture
def user_data():
    """테스트용 사용자 데이터"""
    return {"email": "test@example.com", "password": "Test123!", "nickname": "테스터", "bio": "테스트 사용자입니다"}


@pytest.fixture
def create_user(db, user_data):
    """테스트 사용자 생성"""
    user = User.objects.create_user(
        email=user_data["email"],
        password=user_data["password"],
        nickname=user_data["nickname"],
        bio=user_data.get("bio", ""),
    )
    return user


@pytest.fixture
def create_organizer(db):
    """모임 주최자 생성"""
    return User.objects.create_user(
        email="organizer@example.com", password="Organizer123!", nickname="주최자", bio="모임 주최자"
    )


@pytest.fixture
def create_member_user(db):
    """일반 멤버 사용자 생성"""
    return User.objects.create_user(email="member@example.com", password="Member123!", nickname="멤버", bio="일반 멤버")


@pytest.fixture
def jwt_token(create_user):
    """JWT 토큰 생성"""
    refresh = RefreshToken.for_user(create_user)
    return str(refresh.access_token)


@pytest.fixture
def auth_headers(jwt_token):
    """인증 헤더"""
    return {"HTTP_AUTHORIZATION": f"Bearer {jwt_token}"}


@pytest.fixture
def meetup_data():
    """테스트용 모임 데이터"""
    from datetime import date, timedelta

    return {
        "name": "테스트 모임",
        "description": "테스트를 위한 모임입니다",
        "place": "서울",
        "placeDescription": "강남역 근처",
        "startedAt": (date.today() + timedelta(days=7)).isoformat(),
        "endedAt": (date.today() + timedelta(days=14)).isoformat(),
        "adTitle": "테스트 광고",
        "adEndedAt": (date.today() + timedelta(days=3)).isoformat(),
        "isPublic": True,
        "category": "스터디",
    }


@pytest.fixture
def create_meetup(db, create_organizer, meetup_data):
    """테스트 모임 생성"""
    from datetime import date, timedelta

    meetup = Meetup.objects.create(
        name=meetup_data["name"],
        description=meetup_data["description"],
        place=meetup_data["place"],
        place_description=meetup_data["placeDescription"],
        started_at=date.today() + timedelta(days=7),
        ended_at=date.today() + timedelta(days=14),
        ad_title=meetup_data["adTitle"],
        ad_ended_at=date.today() + timedelta(days=3),
        is_public=meetup_data["isPublic"],
        category=meetup_data["category"],
        organizer=create_organizer,
    )

    # 주최자를 멤버로 추가
    MemberModel.objects.create(user=create_organizer, meetup=meetup, role=MemberModel.MemberRole.ORGANIZER.value)

    return meetup


@pytest.fixture
def create_meetup_with_member(db, create_meetup, create_member_user):
    """멤버가 있는 모임 생성"""
    MemberModel.objects.create(user=create_member_user, meetup=create_meetup, role=MemberModel.MemberRole.MEMBER.value)
    return create_meetup


class APITestCase:
    """API 테스트를 위한 베이스 클래스"""

    def get_auth_headers(self, user):
        """인증 헤더 생성"""
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def assert_error_response(self, response, status_code, message_contains=None):
        """에러 응답 검증"""
        assert response.status_code == status_code
        if message_contains:
            assert message_contains in response.json().get("detail", "")

    def assert_success_response(self, response, status_code=200):
        """성공 응답 검증"""
        assert response.status_code == status_code
        assert response.json() is not None
