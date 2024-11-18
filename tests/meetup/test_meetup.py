# tests/meetup/test_meetup.py

import pytest
from rest_framework.test import APIClient
from user.models.user import User
from meetup.models import Meetup, Category
from placeholder.utils.enums import APIStatus
from datetime import datetime, timedelta


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def organizer(db):
    return User.objects.create_user(
        email='organizer@example.com',
        password='organizerpassword',
        nickname='주최자',
        bio='모임 주최자입니다.'
    )


@pytest.fixture
def categories(db):
    category1 = Category.objects.create(name='Tech', slug='tech')
    category2 = Category.objects.create(name='Networking', slug='networking')
    return [category1, category2]


@pytest.fixture
def access_token(api_client, organizer):
    response = api_client.post(
        '/api/v1/auth/login',
        data={
            'email': organizer.email,
            'password': 'organizerpassword'
        },
        format='json'
    )
    return response.json()['access']


@pytest.mark.django_db
def test_create_meetup_success(api_client, organizer, access_token, categories):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    payload = {
        "name": "Meetup Name",
        "description": "This is a meetup description.",
        "place": "Seoul",
        "placeDescription": "Central Park",
        "latitude": 37.5665,
        "longitude": 126.9780,
        "startedAt": (datetime.now() + timedelta(days=1)).isoformat(),
        "endedAt": (datetime.now() + timedelta(days=2)).isoformat(),
        "ad_title": "Ad Title",
        "adEndedAt": (datetime.now() + timedelta(days=3)).isoformat(),
        "isPublic": True,
        "image": "http://example.com/image.jpg",
        "category": [categories[0].id, categories[1].id]
    }
    response = api_client.post('/api/v1/meetup/', data=payload, format='json')
    assert response.status_code == APIStatus.SUCCESS.code
    data = response.json()
    assert data['isOrganizer'] == True
    assert data['name'] == "Meetup Name"
    assert data['category'] == ["Tech", "Networking"]


@pytest.mark.django_db
def test_list_meetups(api_client, organizer, access_token, categories):
    # 모임 생성
    meetup1 = Meetup.objects.create(
        organizer=organizer,
        name="Meetup1",
        description="Description1",
        place="Place1",
        place_description="PlaceDesc1",
        latitude=37.5665,
        longitude=126.9780,
        started_at=datetime.now() + timedelta(days=1),
        ended_at=datetime.now() + timedelta(days=2),
        ad_title="Ad Title1",
        ad_ended_at=datetime.now() + timedelta(days=3),
        is_public=True,
        image="http://example.com/image1.jpg"
    )
    meetup1.category.set(categories)

    meetup2 = Meetup.objects.create(
        organizer=organizer,
        name="Meetup2",
        description="Description2",
        place="Place2",
        place_description="PlaceDesc2",
        latitude=37.5665,
        longitude=126.9780,
        started_at=datetime.now() + timedelta(days=4),
        ended_at=datetime.now() + timedelta(days=5),
        ad_title="Ad Title2",
        ad_ended_at=datetime.now() + timedelta(days=6),
        is_public=False,
        image="http://example.com/image2.jpg"
    )
    meetup2.category.set(categories)

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = api_client.get('/api/v1/meetup/')
    assert response.status_code == APIStatus.SUCCESS.code
    data = response.json()
    assert len(data) == 2


@pytest.mark.django_db
def test_get_meetup_detail(api_client, organizer, access_token, categories):
    meetup = Meetup.objects.create(
        organizer=organizer,
        name="Meetup1",
        description="Description1",
        place="Place1",
        place_description="PlaceDesc1",
        latitude=37.5665,
        longitude=126.9780,
        started_at=datetime.now() + timedelta(days=1),
        ended_at=datetime.now() + timedelta(days=2),
        ad_title="Ad Title1",
        ad_ended_at=datetime.now() + timedelta(days=3),
        is_public=True,
        image="http://example.com/image1.jpg"
    )
    meetup.category.set(categories)

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = api_client.get(f'/api/v1/meetup/{meetup.id}')
    assert response.status_code == APIStatus.SUCCESS.code  # 200
    data = response.json()
    assert data['isOrganizer'] == True
    assert data['category'] == ["Tech", "Networking"]


@pytest.mark.django_db
def test_update_meetup_success(api_client, organizer, access_token, categories):
    meetup = Meetup.objects.create(
        organizer=organizer,
        name="Meetup1",
        description="Description1",
        place="Place1",
        place_description="PlaceDesc1",
        latitude=37.5665,
        longitude=126.9780,
        started_at=datetime.now() + timedelta(days=1),
        ended_at=datetime.now() + timedelta(days=2),
        ad_title="Ad Title1",
        ad_ended_at=datetime.now() + timedelta(days=3),
        is_public=True,
        image="http://example.com/image1.jpg"
    )
    meetup.category.set(categories)

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    payload = {
        "name": "Meetup1",  # 필수 필드 유지
        "description": "Updated Description",
        "place": "Seoul",
        "placeDescription": "Updated Place Description",
        "latitude": 37.5665,
        "longitude": 126.9780,
        "startedAt": (datetime.now() + timedelta(days=1)).isoformat(),
        "endedAt": (datetime.now() + timedelta(days=2)).isoformat(),
        "ad_title": "Updated Ad Title",
        "adEndedAt": (datetime.now() + timedelta(days=3)).isoformat(),
        "isPublic": True,
        "image": "http://example.com/image1.jpg",
        "category": [categories[0].id]  # 변경된 카테고리
    }
    response = api_client.put(f'/api/v1/meetup/{meetup.id}', data=payload, format='json')
    assert response.status_code == APIStatus.SUCCESS.code  # 200
    data = response.json()
    assert data['description'] == "Updated Description"
    assert data['ad_title'] == "Updated Ad Title"
    assert data['category'] == ["Tech"]  # 변경된 카테고리 확인


@pytest.mark.django_db
def test_delete_meetup_success(api_client, organizer, access_token, categories):
    meetup = Meetup.objects.create(
        organizer=organizer,
        name="Meetup1",
        description="Description1",
        place="Place1",
        place_description="PlaceDesc1",
        latitude=37.5665,
        longitude=126.9780,
        started_at=datetime.now() + timedelta(days=1),
        ended_at=datetime.now() + timedelta(days=2),
        ad_title="Ad Title1",
        ad_ended_at=datetime.now() + timedelta(days=3),
        is_public=True,
        image="http://example.com/image1.jpg"
    )
    meetup.category.set(categories)

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = api_client.delete(f'/api/v1/meetup/{meetup.id}')
    assert response.status_code == 204
    assert not Meetup.objects.filter(id=meetup.id).exists()


@pytest.mark.django_db
def test_create_meetup_unauthorized(api_client, categories):
    payload = {
        "name": "Meetup Name",
        "description": "This is a meetup description.",
        "place": "Seoul",
        "placeDescription": "Central Park",
        "latitude": 37.5665,
        "longitude": 126.9780,
        "startedAt": (datetime.now() + timedelta(days=1)).isoformat(),
        "endedAt": (datetime.now() + timedelta(days=2)).isoformat(),
        "ad_title": "Ad Title",
        "adEndedAt": (datetime.now() + timedelta(days=3)).isoformat(),
        "isPublic": True,
        "image": "http://example.com/image.jpg",
        "category": [categories[0].id, categories[1].id]
    }
    response = api_client.post('/api/v1/meetup/', data=payload, format='json')
    assert response.status_code == APIStatus.UNAUTHORIZED.code
