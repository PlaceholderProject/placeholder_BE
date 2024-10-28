# PlaceHolder BE

## 목차
- [소개](#소개)
  - [내용](#내용)
- [기술 스택](#기술-스택)
- [설치 방법](#설치)
  - [초기 세팅](#초기-세팅)
  - [로컬 서버 실행](#로컬-서버-실행)
  - [pytest 실행](#pytest-실행)
  - [pre-commit 실행](#pre-commit-실행)

## 소개
이 프로젝트는 지도를 이용한 모임 웹 사이트 구현을 위해 만들어졌습니다.

### 내용
- 지역, 관심사, 연령 등의 기준을 정하거나 개개인의 자유료운 주제에 맞춰 새로운 멤버들을 모집하고 만남을 가질 수 있습니다.
- 모임 정보를 검색할 수 있는 플랫폼 역할을 수행합니다.
- 모임 관련 의견을 나누는 커뮤니티의 기능을 제공합니다
- 스케줄을 짜고 추억을 남기는 기록 페이지로 활용할 수 있습니다.

## 기술 스택
- Django: 강력한 사용성과 편의성 (마이그레이션, ORM, 관리자 페이지 등)
- Django-ninja: DRF보다 빠른 api 응답 지원
- pydjantic: DRF의 serializer보다 빠른 검증, 직렬화 지원
- poetry: 각 라이브러리의 의존성 관리
- pytest: django test에 비해 많은 기능 제공 (Fixture, Assertion, mock, parametrize 등)
- pre-commit: 코드의 일관성을 관리 (black, flack8, isort, cspell)
- postgreSQL: django에서 가장 많은 기능을 지원하는 DB, postGIS 확장을 사용해 공간데이터 관리

## 설치

### 초기 세팅
- 프로젝트를 가져올 폴더로 이동합니다.
- 파이썬 버전(3.12.4)을 확인하고 가상환경을 만듭니다. pyenv 사용을 권장합니다.
```bash
$ pyenv local 3.12.4
$ python -V
$ python -m venv venv
```
- 가상환경 활성화
```bash
$ source venv/bin/activate
```
현재 폴더에 프로젝트를 설치
```bash
$ git clone https://github.com/PlaceholderProject/placeholder_BE.git .
```
- 환경 변수 설정(환경 변수 파일은 문의해주세요)
```bash
$ source local.env.sh
```
- 의존성 및 pre-commit 설치
```bash
$ pip install poetry
$ poetry install
$ pre-commit install
```
- (Option) postgreSQL, postGIS 설치
```bash
$ brew install postgresql
$ brew install postgis
```
- local db 생성 및 postGIS 확장 적용
```bash
$ psql -U postgres
$ create database placeholder;
$ \c placeholder
$ create extension postgis;
$ \q
```
- db 마이그레이션
```bash
$ python manage.py migrate
```
- django superuser 생성
```bash
$ python manage.py createsuperuser
```

### 로컬 서버 실행
```bash
$ python manage.py runserver localhost:8000
```

### pytest 실행
```bash
$ pytest
```

### pre-commit 실행
```bash
$ pre-commit run
```
