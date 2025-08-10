# 테스트 가이드

이 프로젝트의 pytest 기반 테스트 가이드입니다.

## 📁 테스트 구조

```
tests/
├── conftest.py              # 공통 픽스처 및 설정
├── test_integration.py      # 통합 테스트
├── test_utils.py           # 유틸리티 테스트
├── user/
│   ├── test_models.py      # User 모델 테스트
│   └── test_auth.py        # 인증 API 테스트
└── meetup/
    ├── test_models.py      # Meetup 모델 테스트
    ├── meetup.py           # Meetup API 테스트 (기존)
    └── test_member.py      # Member 관련 테스트
```

## 🚀 테스트 실행 방법

### 기본 명령어

```bash
# 모든 테스트 실행
pytest

# 또는 Makefile 사용
make test
```

### 특정 테스트 실행

```bash
# 특정 파일 테스트
pytest tests/user/test_models.py

# 특정 클래스 테스트
pytest tests/user/test_models.py::TestUserModel

# 특정 메서드 테스트
pytest tests/user/test_models.py::TestUserModel::test_create_user_success

# 키워드로 필터링
pytest -k "user and model"
pytest -k "not integration"
```

### 마커 기반 테스트

```bash
# 단위 테스트만 실행
pytest -m unit

# API 테스트만 실행
pytest -m api

# 통합 테스트만 실행
pytest -m integration

# 느린 테스트 제외
pytest -m "not slow"
```

### 앱별 테스트

```bash
# User 관련 테스트
make test-user
pytest tests/user/

# Meetup 관련 테스트
make test-meetup
pytest tests/meetup/

# 모델 테스트만
make test-models
pytest tests/*/test_models.py
```

## 📊 커버리지 리포트

```bash
# 커버리지 포함 테스트 실행
make test-coverage

# 또는 직접 실행
pytest --cov=. --cov-report=html --cov-report=term-missing

# HTML 리포트 확인
open htmlcov/index.html
```

## 🔧 픽스처 사용법

### 기본 픽스처

```python
def test_example(create_user, create_meetup, api_client):
    # create_user: 테스트 사용자
    # create_meetup: 테스트 모임 (주최자 포함)
    # api_client: Django test client
    pass
```

### 인증이 필요한 테스트

```python
def test_authenticated_request(create_user, api_client):
    from tests.conftest import APITestCase

    test_case = APITestCase()
    headers = test_case.get_auth_headers(create_user)

    response = api_client.post(
        "/api/v1/meetup",
        data=json.dumps(data),
        content_type="application/json",
        **headers
    )
```

## 🏷️ 테스트 마커

테스트에 마커를 추가하여 분류할 수 있습니다:

```python
import pytest

@pytest.mark.unit
def test_model_creation():
    pass

@pytest.mark.api
@pytest.mark.slow
def test_complex_api():
    pass

@pytest.mark.integration
def test_full_workflow():
    pass
```

## 🗄️ 데이터베이스 설정

- `--reuse-db`: 테스트 DB 재사용으로 속도 향상
- `--nomigrations`: 마이그레이션 건너뛰기
- 각 테스트는 트랜잭션으로 격리됨

## 📝 테스트 작성 가이드

### 1. 네이밍 컨벤션

- 파일: `test_*.py` 또는 `*_test.py`
- 클래스: `Test*`
- 함수: `test_*`

### 2. 테스트 구조 (AAA 패턴)

```python
def test_something():
    # Arrange (준비)
    user = create_user_function()
    data = {"key": "value"}

    # Act (실행)
    result = function_to_test(user, data)

    # Assert (검증)
    assert result.status_code == 200
    assert result.data["key"] == "value"
```

### 3. 테스트 독립성

- 각 테스트는 독립적이어야 함
- 픽스처를 활용하여 초기 데이터 준비
- 테스트 간 의존성 금지

### 4. Mock 사용

```python
from unittest.mock import patch, MagicMock

@patch('module.function')
def test_with_mock(mock_function):
    mock_function.return_value = "mocked_value"
    # 테스트 로직
```

## 🚨 주의사항

1. **테스트 DB**: 자동으로 생성/삭제되므로 실제 데이터 손실 없음
2. **외부 의존성**: AWS S3 등은 Mock으로 처리
3. **환경변수**: 테스트용 설정 사용 (`settings.local`)
4. **성능**: 느린 테스트는 `@pytest.mark.slow` 마커 추가

## 🔍 디버깅

```bash
# 상세한 출력
pytest -v -s

# 실패 시 즉시 중단
pytest -x

# 마지막 실패 테스트만 재실행
pytest --lf

# 실패한 테스트 디버깅
pytest --pdb
```

## ⚡ 성능 최적화

- `--reuse-db`: 데이터베이스 재사용
- `--nomigrations`: 마이그레이션 건너뛰기
- `pytest-xdist`: 병렬 실행 (별도 설치 필요)

```bash
pip install pytest-xdist
pytest -n auto  # CPU 코어 수만큼 병렬 실행
```
