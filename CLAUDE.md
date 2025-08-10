# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django REST API project for a meetup/event management platform with the following key features:
- User authentication and profiles
- Meetup creation and management
- Member management for meetups
- Proposal system for meetup activities
- Schedule management
- Comment system for meetups and schedules
- Notification system
- AWS S3 integration for media files

## Development Commands

### Environment Setup
```bash
# Install dependencies using Poetry
poetry install

# Or using pip
pip install -r requirements.txt

# Activate virtual environment (if using venv)
source venv/bin/activate
```

### Database Operations
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development Server
```bash
# Run development server
python manage.py runserver

# Run with specific settings
python manage.py runserver --settings=placeholder.settings.local
```

### Testing
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -s

# Run specific test file
pytest tests/meetup/meetup.py

# Run specific test
pytest tests/meetup/meetup.py::test_function_name
```

### Code Quality
```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check code style with flake8
flake8

# Run pre-commit hooks
pre-commit run --all-files
```

## Architecture

### Core Applications
- **user**: User authentication, profiles, and user management
- **meetup**: Core meetup functionality, member management, proposals, schedules
- **notification**: Notification system for user alerts

### Key Technologies
- **Django 5.2.2** with **django-ninja** for API framework
- **PostgreSQL** as the database
- **JWT authentication** via django-rest-framework-simplejwt
- **AWS S3** for media file storage
- **Pydantic** for data validation and serialization

### API Structure
- Main API router defined in `placeholder/apis.py`
- All APIs accessible via `/api/v1/` prefix
- Uses django-ninja with automatic OpenAPI documentation at `/api/v1/docs`

### Database Models
- **BaseModel**: Abstract base with `created_at` and `updated_at` timestamps
- **Custom User model**: Email-based authentication with nickname field
- **Modular design**: Each app has its own models, schemas, and APIs

### Settings Configuration
- **Base settings**: `placeholder/settings/base.py`
- **Local development**: `placeholder/settings/local.py`
- **Production**: `placeholder/settings/prod.py`
- Environment variables handled via django-environ

### Media Handling
- Local development: Files stored in `media/` directory
- Production: AWS S3 integration for scalable file storage

### Authentication
- JWT-based authentication with 1-day token lifetime
- Custom User model with email as USERNAME_FIELD
- Korean localization (ko-KR, Asia/Seoul timezone)

### API Response Format
- Standardized error handling via global exception handler
- Custom APIStatus enum for consistent response codes and messages
- Swagger documentation enabled for API exploration
