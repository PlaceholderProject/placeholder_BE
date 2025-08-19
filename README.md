# 🎯 Placeholder - 모임 관리 API

> **Django Ninja 기반의 REST API 모임 관리 서비스**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2.2-green.svg)](https://djangoproject.com)
[![Django Ninja](https://img.shields.io/badge/Django%20Ninja-1.4.3-red.svg)](https://django-ninja.rest-framework.com)
[![Tests](https://img.shields.io/badge/Tests-90%20passed-brightgreen.svg)](#테스트)

**Placeholder**는 모임 생성, 참여 신청, 멤버 관리, 스케줄 관리 등을 지원하는 Django Ninja 기반의 REST API 서비스입니다.

## 🌐 **API 문서**

- **Swagger UI**: `/api/v1/docs`
- **OpenAPI Schema**: `/api/v1/openapi.json`

---

## ✨ **주요 기능**

### **모임 관리**
- 모임 생성, 수정, 삭제
- 검색 및 필터링 (키워드, 카테고리, 지역)
- 공개/비공개 설정
- 좋아요 기능

### **참여 시스템**
- 참여 신청서 제출
- 주최자 승인/거절 시스템
- 참여 상태 관리 (대기, 승인, 거절, 무시)
- 멤버 역할 관리 (주최자/멤버)

### **소통 기능**
- 모임 댓글
- 스케줄별 댓글
- 실시간 알림 시스템

### **스케줄 관리**
- 모임별 일정 생성 및 관리
- 참석자 관리

### **사용자 관리**
- JWT 기반 인증
- 프로필 관리
- 이메일/닉네임 중복 확인

---

## 🛠️ **기술 스택**

### **Backend**
- **Django 5.2.2**: 웹 프레임워크
- **Django Ninja 1.4.3**: REST API 개발
- **PostgreSQL**: 데이터베이스
- **JWT**: 인증 시스템

### **Storage & Files**
- **AWS S3**: 이미지 파일 저장
- **Pillow**: 이미지 처리

### **Development Tools**
- **Poetry**: 의존성 관리
- **pytest**: 테스트 프레임워크 (90개 테스트)
- **Black + isort**: 코드 포매팅
- **flake8**: 린팅
- **pre-commit**: Git hooks

### **Deployment**
- **Gunicorn + Uvicorn**: ASGI 서버
- **Nginx**: 리버스 프록시
- **systemd**: 서비스 관리
- **Let's Encrypt**: SSL 인증서

---

## 🏗️ **프로젝트 구조**

```
placeholder/
├── user/              # 사용자 인증 및 관리
├── meetup/            # 모임 관리 (핵심 기능)
│   ├── models/        # 데이터베이스 모델
│   ├── apis/          # REST API 엔드포인트
│   └── schemas/       # 요청/응답 스키마
├── notification/      # 알림 시스템
├── placeholder/       # 설정 및 공통 유틸리티
│   ├── settings/      # 환경별 설정
│   └── utils/         # 인증, S3, 예외처리
├── tests/             # 테스트 코드 (90개)
└── etc/               # 시스템 설정 파일
```

---

## 🚀 **설치 및 실행**

### **요구사항**
- Python 3.12+
- PostgreSQL
- Poetry 또는 pip

### **설치**
```bash
# 저장소 클론
git clone <repository-url>
cd placeholder

# 의존성 설치
poetry install
# 또는 pip install -r requirements.txt

# 환경 변수 설정
source local.env.sh

# 데이터베이스 마이그레이션
python manage.py migrate

# 개발 서버 실행
python manage.py runserver
```

### **Makefile 사용 (24개 명령어)**
```bash
# 개발 환경 설정
make setup-dev

# 테스트 실행
make test

# 코드 포매팅
make format

# 서버 실행
make run
```

---

## 📖 **API 가이드**

### **인증**
```bash
# 로그인
curl -X POST "/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# 인증이 필요한 요청
curl -H "Authorization: Bearer <token>" "/api/v1/meetup/"
```

### **주요 엔드포인트**
```http
# 인증
POST   /api/v1/auth/login          # 로그인
POST   /api/v1/auth/refresh        # 토큰 갱신
POST   /api/v1/auth/email          # 이메일 중복 확인
POST   /api/v1/auth/nickname       # 닉네임 중복 확인

# 모임 관리
GET    /api/v1/meetup/             # 모임 목록 조회
POST   /api/v1/meetup/             # 모임 생성
GET    /api/v1/meetup/{id}         # 모임 상세 조회
PUT    /api/v1/meetup/{id}         # 모임 수정
DELETE /api/v1/meetup/{id}         # 모임 삭제
POST   /api/v1/meetup/{id}/like    # 좋아요 토글

# 참여 관리
GET    /api/v1/proposal/           # 참여 신청 목록
POST   /api/v1/proposal/           # 참여 신청
POST   /api/v1/proposal/{id}/acceptance  # 신청 승인
POST   /api/v1/proposal/{id}/refuse      # 신청 거절

# 멤버 관리
GET    /api/v1/meetup/{id}/member  # 멤버 목록
DELETE /api/v1/member/{id}         # 멤버 삭제

# 스케줄 관리
GET    /api/v1/schedule/           # 스케줄 목록
POST   /api/v1/schedule/           # 스케줄 생성
PUT    /api/v1/schedule/{id}       # 스케줄 수정
DELETE /api/v1/schedule/{id}       # 스케줄 삭제

# 댓글
GET    /api/v1/meetup-comment/     # 모임 댓글 조회
POST   /api/v1/meetup-comment/     # 모임 댓글 작성
GET    /api/v1/schedule-comment/   # 스케줄 댓글 조회
POST   /api/v1/schedule-comment/   # 스케줄 댓글 작성

# 알림
GET    /api/v1/notification/       # 알림 목록
PUT    /api/v1/notification/{id}   # 알림 읽음 처리
```

---

## 🧪 **테스트**

### **테스트 현황**
- **총 테스트 수**: 90개
- **통과율**: 100%
- **테스트 파일**: 10개

### **테스트 실행**
```bash
# 전체 테스트
make test
pytest

# 앱별 테스트
make test-user
make test-meetup

# 커버리지 포함
make test-coverage
```

### **테스트 구조**
```
tests/
├── conftest.py              # 공통 픽스처
├── user/
│   ├── test_auth.py        # 인증 API 테스트
│   └── test_models.py      # 사용자 모델 테스트
├── meetup/
│   ├── test_meetup_api.py  # 모임 API 테스트
│   ├── test_member.py      # 멤버 기능 테스트
│   └── test_models.py      # 모임 모델 테스트
├── test_utils.py           # 유틸리티 테스트
└── test_integration.py     # 통합 테스트
```

---

## 🗄️ **데이터베이스 모델**

### **주요 모델 관계**
```
User ─1:N─ Meetup (organizer)
User ─M:N─ Meetup (members via Member)
User ─1:N─ Proposal
User ─1:N─ Notification
Meetup ─1:N─ Schedule
Meetup ─1:N─ MeetupComment
Schedule ─1:N─ ScheduleComment
```

### **핵심 모델**
- **User**: 사용자 정보 (email, nickname, bio, image)
- **Meetup**: 모임 정보 (이름, 설명, 장소, 날짜, 카테고리)
- **Member**: 모임 멤버 (역할: ORGANIZER/MEMBER)
- **Proposal**: 참여 신청 (상태: PENDING/ACCEPTANCE/REFUSE/IGNORE)
- **Schedule**: 모임 일정
- **Notification**: 알림

---

## 🌐 **배포**

### **시스템 구성**
```
Internet → Nginx → Gunicorn → Django App
                     ↓
              PostgreSQL Database
                     ↓
                AWS S3 (Static Files)
```

### **배포 파일**
- **systemd**: `/etc/systemd/system/gunicorn.service`
- **Nginx**: `/etc/nginx/sites-available/placeholder`
- **SSL**: Let's Encrypt 인증서

### **배포 설정**
```bash
# 프로덕션 환경 변수
export DJANGO_SETTINGS_MODULE=placeholder.settings.prod
export DEBUG=False

# 정적 파일 수집
python manage.py collectstatic

# 서비스 시작
systemctl start gunicorn
systemctl start nginx
```

---

## 🔧 **개발 가이드**

### **코드 스타일**
- **Black**: 코드 포매팅
- **isort**: import 정렬
- **flake8**: 린팅
- **Pre-commit**: 자동 검사

### **개발 워크플로우**
```bash
# 새 기능 개발
git checkout -b feature/new-feature

# 코드 품질 검사
make format
make lint
make test

# 커밋
git commit -m "feat: add new feature"
```

### **새 기능 추가 순서**
1. **모델 정의**: `models/`에 데이터베이스 모델 추가
2. **API 구현**: `apis/`에 엔드포인트 구현
3. **스키마 정의**: `schemas/`에 요청/응답 스키마
4. **테스트 작성**: `tests/`에 테스트 케이스 추가
5. **문서 확인**: Swagger UI에서 자동 생성된 문서 확인

---

## ⚙️ **설정**

### **환경별 설정**
- **로컬**: `placeholder.settings.local`
- **프로덕션**: `placeholder.settings.prod`

### **필수 환경 변수**
```bash
DJANGO_SETTINGS_MODULE=placeholder.settings.local
SECRET_KEY=your-secret-key
DEBUG=True

# 데이터베이스
DB_NAME=placeholder
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# AWS S3 (선택사항)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_MEDIA_BUCKET_NAME=your-bucket
```

---

## 🐛 **알려진 이슈**

### **API 설계 개선점**
현재 API 구조에서 RESTful 원칙에 맞지 않는 부분들이 있습니다:

1. **액션 기반 URL**
   ```
   POST /api/v1/proposal/{id}/acceptance  # 개선 필요
   POST /api/v1/proposal/{id}/refuse      # 개선 필요
   ```

2. **중첩 리소스 불일치**
   ```
   /api/v1/member      # 독립적으로 분리됨
   /api/v1/proposal    # 모임과 분리됨
   ```

향후 버전에서 RESTful 원칙에 맞게 개선 예정입니다.

---

## 📈 **향후 계획**

### **개선 사항**
- [ ] RESTful API 구조 개선
- [ ] 실시간 채팅 기능
- [ ] 이미지 최적화
- [ ] 캐싱 시스템 도입
- [ ] API 성능 최적화

### **새 기능**
- [ ] 모임 추천 시스템
- [ ] 캘린더 연동
- [ ] 모바일 앱 지원

---

## 🤝 **기여하기**

### **개발 환경 설정**
```bash
# 개발 환경 설정
make setup-dev

# Pre-commit 훅 설치
pre-commit install

# 테스트 실행
make test
```

### **기여 가이드라인**
1. Issue 확인 후 새 브랜치 생성
2. 기능 구현 및 테스트 작성
3. 코드 스타일 검사 통과
4. Pull Request 생성

### **코드 리뷰 체크리스트**
- [ ] 모든 테스트 통과
- [ ] 린팅 통과 (flake8, black, isort)
- [ ] 새 기능에 대한 테스트 포함
- [ ] API 문서 자동 업데이트 확인

---

## 📄 **라이선스**

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.

---

## 📞 **지원**

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **API 문서**: `/api/v1/docs`에서 상세한 API 명세 확인

---

## 🙏 **오픈소스 라이브러리**

이 프로젝트는 다음 오픈소스 라이브러리를 사용합니다:

- [Django](https://djangoproject.com) - 웹 프레임워크
- [Django Ninja](https://django-ninja.rest-framework.com) - API 프레임워크
- [PostgreSQL](https://postgresql.org) - 데이터베이스
- [pytest](https://pytest.org) - 테스트 프레임워크
