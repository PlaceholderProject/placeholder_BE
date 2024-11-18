import pytest
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from user.models.user import User
from placeholder.utils.enums import APIStatus


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='testpassword',
        nickname='testuser',
        bio='안녕하세요'
    )


@pytest.mark.django_db
def test_register_success(api_client):
    response = api_client.post(
        '/api/v1/auth/register',
        data={
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'nickname': 'newuser',
            'bio': '새로운 사용자입니다.',
        },
        format='json'
    )
    assert response.status_code == APIStatus.SUCCESS.code
    assert 'access' in response.json()
    assert 'refresh' in response.json()


@pytest.mark.django_db
def test_register_existing_email(api_client, user):
    response = api_client.post(
        '/api/v1/auth/register',
        data={
            'email': user.email,  # 이미 존재하는 이메일
            'password': 'newpassword',
            'nickname': 'nickname',
            'bio': '새로운 사용자입니다.'
        },
        format='json'
    )
    assert response.status_code == APIStatus.EMAIL_ALREADY_EXISTS.code
    assert response.json()['detail'] == APIStatus.EMAIL_ALREADY_EXISTS.message


@pytest.mark.django_db
def test_register_existing_nickname(api_client, user):
    response = api_client.post(
        '/api/v1/auth/register',
        data={
            'email': 'unique@example.com',
            'password': 'newpassword',
            'nickname': user.nickname,  # 이미 존재하는 닉네임
            'bio': '새로운 사용자입니다.'
        },
        format='json'
    )
    assert response.status_code == APIStatus.NICKNAME_ALREADY_EXISTS.code
    assert response.json()['detail'] == APIStatus.NICKNAME_ALREADY_EXISTS.message


@pytest.mark.django_db
def test_register_invalid_data(api_client):
    # 이메일 형식이 잘못된 경우
    response = api_client.post(
        '/api/v1/auth/register',
        data={
            'email': 'invalidemail',
            'password': 'short',
            'nickname': 'nu',
            'bio': 'a' * 41  # bio 최대 길이 초과
        },
        format='json'
    )
    assert response.status_code == APIStatus.UNPROCESSABLE.code


@pytest.mark.django_db
def test_login_success(api_client, user):
    response = api_client.post(
        '/api/v1/auth/login',
        data={
            'email': user.email,
            'password': 'testpassword'
        },
        format='json'
    )
    assert response.status_code == APIStatus.SUCCESS.code
    assert 'access' in response.json()
    assert 'refresh' in response.json()


@pytest.mark.django_db
def test_login_wrong_credentials(api_client):
    response = api_client.post(
        '/api/v1/auth/login',
        data={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        },
        format='json'
    )
    assert response.status_code == APIStatus.INVALID_CREDENTIALS.code
    assert response.json()['detail'] == APIStatus.INVALID_CREDENTIALS.message


@pytest.mark.django_db
def test_login_missing_fields(api_client):
    # 비밀번호가 없는 경우
    response = api_client.post(
        '/api/v1/auth/login',
        data={
            'email': 'test@example.com',
        },
        format='json'
    )
    assert response.status_code == APIStatus.UNPROCESSABLE.code


@pytest.mark.django_db
def test_token_refresh_success(api_client, user):
    # 로그인하여 refresh 토큰 획득
    response = api_client.post(
        '/api/v1/auth/login',
        data={
            'email': user.email,
            'password': 'testpassword'
        },
        format='json'
    )
    refresh_token = response.json()['refresh']

    # 토큰 갱신
    response = api_client.post(
        '/api/v1/auth/refresh',
        data={'refresh': refresh_token},
        format='json'
    )
    assert response.status_code == APIStatus.SUCCESS.code
    assert 'access' in response.json()


@pytest.mark.django_db
def test_token_refresh_invalid_token(api_client):
    response = api_client.post(
        '/api/v1/auth/refresh',
        data={'refresh': 'invalidtoken'},
        format='json'
    )
    assert response.status_code == APIStatus.INVALID_TOKEN.code
    assert response.json()['detail'] == APIStatus.INVALID_TOKEN.message


@pytest.mark.django_db
def test_profile_success(api_client, user):
    # 로그인하여 액세스 토큰 획득
    response = api_client.post(
        '/api/v1/auth/login',
        data={
            'email': user.email,
            'password': 'testpassword'
        },
        format='json'
    )
    access_token = response.json()['access']

    # 프로필 조회
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = api_client.get('/api/v1/auth/profile')
    assert response.status_code == APIStatus.SUCCESS.code
    data = response.json()
    assert data['email'] == user.email
    assert data['nickname'] == user.nickname
    assert data['bio'] == user.bio


@pytest.mark.django_db
def test_profile_unauthorized(api_client):
    # 토큰 없이 프로필 조회
    response = api_client.get('/api/v1/auth/profile')
    assert response.status_code == APIStatus.UNAUTHORIZED.code


@pytest.mark.django_db
def test_profile_invalid_token(api_client):
    # 잘못된 토큰으로 프로필 조회
    api_client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
    response = api_client.get('/api/v1/auth/profile')
    assert response.status_code == APIStatus.INVALID_TOKEN.code
