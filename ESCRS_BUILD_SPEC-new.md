# Enhanced Student Course Recommendation System (ESCRS)
## LLM Build Specification — Next.js Frontend (local) + Python/Django Backend (Docker)

> **How to use this document:** Feed this file to your LLM as the primary context before starting any implementation. Work through each section in order. Each section contains the exact structure, models, API contracts, and component specs needed. Do not deviate from the file/folder naming conventions or the API endpoint paths — the frontend and backend are wired together against these exact contracts.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Repository Structure](#3-repository-structure)
4. [Environment Variables](#4-environment-variables)
5. [Backend — Django](#5-backend--django)
   - [5.1 Project Bootstrap](#51-project-bootstrap)
   - [5.2 Database Models](#52-database-models)
   - [5.3 API Endpoints](#53-api-endpoints)
   - [5.4 Recommendation Engine](#54-recommendation-engine)
   - [5.5 Authentication](#55-authentication)
   - [5.6 Celery Tasks](#56-celery-tasks)
6. [Frontend — Next.js](#6-frontend--nextjs)
   - [6.1 Project Bootstrap](#61-project-bootstrap)
   - [6.2 Directory Structure](#62-directory-structure)
   - [6.3 Global Config](#63-global-config)
   - [6.4 Pages & Routes](#64-pages--routes)
   - [6.5 Components](#65-components)
   - [6.6 State Management](#66-state-management)
   - [6.7 API Client](#67-api-client)
7. [Data Contracts (Shared Types)](#7-data-contracts-shared-types)
8. [Recommendation Engine Logic](#8-recommendation-engine-logic)
9. [Testing Requirements](#9-testing-requirements)
10. [Docker & Deployment](#10-docker--deployment)
11. [Implementation Order](#11-implementation-order)

---

## 1. Project Overview

**What it is:** A web application that recommends the top 5 most relevant university courses to each student using a hybrid machine learning engine combining Collaborative Filtering (CF) and Content-Based Filtering (CBF).

**Core problem it solves:** Academic advising does not scale with enrollment. Students receive generic course guidance. This system mines LMS behavioral data (clicks, time spent, enrollment history) to deliver personalized, ranked recommendations automatically.

**Two user roles:**
- **Student** — views recommendations, rates them, browses the course catalog, manages their academic profile and interests
- **Admin** — manages courses and syllabi, monitors recommendation accuracy metrics, configures the hybrid engine weight

**The hybrid scoring formula:**
```
S_hybrid = W × S_cf + (1 - W) × S_cbf
```
Where `W` is a float between 0.0 and 1.0 configured by the admin. When a student has fewer than 3 course interactions (cold-start condition), the system falls back to pure CBF (W = 0).

---

## 2. Tech Stack

### Backend
| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.11+ |
| Framework | Django | 4.2 LTS |
| API | Django REST Framework | 3.15+ |
| Auth | djangorestframework-simplejwt | 5.3+ |
| ML / Recommendation | scikit-learn, scipy, pandas, numpy | latest stable |
| Database | PostgreSQL | 15+ |
| Cache / Broker | Redis | 7+ |
| Task Queue | Celery | 5.3+ |
| File Storage | AWS S3 (via boto3) or local filesystem | — |
| Containerization | Docker + Docker Compose | — |

### Frontend
| Layer | Technology | Version |
|---|---|---|
| Framework | Next.js (App Router) | 14+ |
| Language | TypeScript | 5+ |
| Styling | Tailwind CSS | 3.4+ |
| UI Components | shadcn/ui | latest |
| State | Zustand | 4+ |
| Server State | TanStack Query (React Query) | 5+ |
| Forms | React Hook Form + Zod | latest |
| Charts | Recharts | 2+ |
| Auth | NextAuth.js (Auth.js v5) | 5+ |
| HTTP Client | Axios | 1+ |
| Testing | Jest + React Testing Library + Playwright | — |

---

## 3. Repository Structure

Use a monorepo with two top-level directories:

```
escrs/
├── backend/                    # Django project
│   ├── config/                 # Django settings package
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── users/              # User model, auth, profiles
│   │   ├── courses/            # Course catalog, syllabi
│   │   ├── recommendations/    # Engine, scoring, results
│   │   ├── interactions/       # LMS behavioral log
│   │   └── analytics/          # Admin metrics
│   ├── engine/                 # Pure Python recommendation logic (no Django deps)
│   │   ├── __init__.py
│   │   ├── collaborative.py
│   │   ├── content_based.py
│   │   ├── hybrid.py
│   │   └── utils.py
│   ├── tasks/                  # Celery task definitions
│   │   ├── __init__.py
│   │   ├── recommendation.py
│   │   └── email.py
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                   # Next.js project
│   ├── src/
│   │   ├── app/                # App Router pages
│   │   ├── components/         # Reusable UI components
│   │   ├── lib/                # Utilities, API client, schemas
│   │   ├── hooks/              # Custom React hooks
│   │   ├── store/              # Zustand stores
│   │   └── types/              # Shared TypeScript types
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   ├── Dockerfile
│   └── .env.example
│
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

---

## 4. Environment Variables

### Backend (`backend/.env`)
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.development

# Database
DATABASE_URL=postgresql://escrs_user:escrs_pass@localhost:5432/escrs_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Recommendation Engine
DEFAULT_HYBRID_WEIGHT=0.6
DEFAULT_TOP_N=5
COLD_START_THRESHOLD=3

# AWS S3 (optional for file storage)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@escrs.edu
```

### Frontend (`frontend/.env.local`)

> **Note:** The frontend runs directly on your machine with `npm run dev`. It is NOT containerized. Both `NEXT_PUBLIC_API_URL` and `API_URL` point to `localhost:8000` because the backend Docker container exposes port 8000 to the host.

```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-here

# Public (browser-accessible) — points to Docker-exposed backend port
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=ESCRS

# Server-side (Next.js API routes / server components)
# Same as NEXT_PUBLIC_API_URL because the frontend runs on the host, not inside Docker
API_URL=http://localhost:8000/api/v1
```

---

## 5. Backend — Django

### 5.1 Project Bootstrap

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install django djangorestframework djangorestframework-simplejwt \
  django-cors-headers django-environ celery redis boto3 \
  scikit-learn scipy pandas numpy psycopg2-binary \
  Pillow python-magic django-filter drf-spectacular

pip freeze > requirements.txt

# Start project
django-admin startproject config .
python manage.py startapp users
python manage.py startapp courses
python manage.py startapp recommendations
python manage.py startapp interactions
python manage.py startapp analytics

# Move apps into apps/ directory
mkdir apps
# (move each app directory into apps/ and update config/settings accordingly)
```

**`config/settings/base.py` — key settings to include:**
```python
from pathlib import Path
import environ

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    # Local
    'apps.users',
    'apps.courses',
    'apps.recommendations',
    'apps.interactions',
    'apps.analytics',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be first
    'django.middleware.security.SecurityMiddleware',
    # ... rest of defaults
]

AUTH_USER_MODEL = 'users.User'  # Custom user model

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 15)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('JWT_REFRESH_TOKEN_LIFETIME_DAYS', 7)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

CELERY_BROKER_URL = env('REDIS_URL')
CELERY_RESULT_BACKEND = env('REDIS_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]
```

---

### 5.2 Database Models

#### `apps/users/models.py`
```python
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        ADMIN = 'admin', 'Admin'

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    program = models.CharField(max_length=100)
    level = models.CharField(max_length=50)  # e.g. "undergraduate", "postgraduate"
    interests = models.JSONField(default=list)  # e.g. ["machine learning", "databases", "networking"]
    completed_course_ids = models.JSONField(default=list)  # list of course IDs
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    onboarding_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_profiles'
```

#### `apps/courses/models.py`
```python
from django.db import models
import numpy as np

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'departments'

    def __str__(self):
        return self.name


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    credits = models.PositiveIntegerField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='courses')
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='prerequisite_for')
    level = models.CharField(max_length=50)  # e.g. "100", "200", "postgraduate"
    syllabus_text = models.TextField(blank=True)  # raw text extracted from uploaded PDF
    syllabus_vector = models.JSONField(default=list)  # TF-IDF float array — stored as JSON list
    syllabus_file = models.FileField(upload_to='syllabi/', null=True, blank=True)
    tags = models.JSONField(default=list)  # manually assigned keyword tags
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'

    def __str__(self):
        return f"{self.code} — {self.title}"

    def get_vector(self):
        return np.array(self.syllabus_vector) if self.syllabus_vector else np.array([])
```

#### `apps/interactions/models.py`
```python
from django.db import models
from apps.users.models import User
from apps.courses.models import Course

class Enrollment(models.Model):
    """Historical enrollment records — one row per student per course completed."""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)
    semester = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'enrollments'
        unique_together = ('student', 'course')


class Interaction(models.Model):
    """LMS behavioral signals — clicks, time on page, last access."""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='interactions')
    clicks = models.PositiveIntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interactions'
        unique_together = ('student', 'course')
```

#### `apps/recommendations/models.py`
```python
from django.db import models
from apps.users.models import User
from apps.courses.models import Course

class RecommendationResult(models.Model):
    """Audit log of every recommendation batch generated."""

    class RecommendationType(models.TextChoices):
        CF = 'CF', 'Collaborative Filtering'
        CBF = 'CBF', 'Content-Based Filtering'
        HYBRID = 'HYBRID', 'Hybrid'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='recommendations')
    score = models.FloatField()
    rank = models.PositiveIntegerField()  # 1 = top recommendation
    recommendation_type = models.CharField(max_length=10, choices=RecommendationType.choices)
    w_weight = models.FloatField()  # the W value used when this was generated
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendation_results'
        ordering = ['rank']


class Feedback(models.Model):
    """Student thumbs up/down on a recommendation."""

    class Rating(models.IntegerChoices):
        POSITIVE = 1, 'Helpful'
        NEGATIVE = -1, 'Not helpful'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    recommendation = models.ForeignKey(RecommendationResult, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.SmallIntegerField(choices=Rating.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedbacks'
        unique_together = ('student', 'recommendation')


class EngineSettings(models.Model):
    """Singleton table storing engine configuration set by admin."""
    hybrid_weight = models.FloatField(default=0.6)  # W value
    top_n = models.PositiveIntegerField(default=5)
    cold_start_threshold = models.PositiveIntegerField(default=3)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'engine_settings'

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj
```

---

### 5.3 API Endpoints

**Base URL:** `/api/v1/`

All endpoints return JSON. All authenticated endpoints require `Authorization: Bearer <access_token>` header.

#### Authentication (`/api/v1/auth/`)

| Method | Path | Body | Response | Auth |
|---|---|---|---|---|
| POST | `/auth/register/` | `{email, password, full_name}` | `{user, tokens}` | Public |
| POST | `/auth/login/` | `{email, password}` | `{access, refresh, user}` | Public |
| POST | `/auth/refresh/` | `{refresh}` | `{access}` | Public |
| POST | `/auth/logout/` | `{refresh}` | `204` | Required |
| POST | `/auth/password-reset/` | `{email}` | `204` | Public |
| POST | `/auth/password-reset/confirm/` | `{token, password}` | `204` | Public |

**Login response shape:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {
    "id": 1,
    "email": "student@miva.edu",
    "full_name": "Idahosa Joshua",
    "role": "student",
    "onboarding_complete": false
  }
}
```

#### Students (`/api/v1/students/`)

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/students/me/` | Get current user's profile | Student |
| PUT | `/students/me/` | Update profile (interests, program, GPA) | Student |
| GET | `/students/me/enrollments/` | List completed courses | Student |
| POST | `/students/me/enrollments/` | Add completed course | Student |
| DELETE | `/students/me/enrollments/{course_id}/` | Remove completed course | Student |
| GET | `/students/me/interactions/` | Get LMS interaction log | Student |
| POST | `/students/me/interactions/` | Log a course interaction (click, time) | Student |

**Student profile response shape:**
```json
{
  "id": 1,
  "email": "student@miva.edu",
  "full_name": "Idahosa Joshua",
  "program": "MIT",
  "level": "postgraduate",
  "interests": ["machine learning", "databases", "cloud computing"],
  "gpa": "3.85",
  "onboarding_complete": true,
  "completed_course_ids": [12, 34, 56],
  "interaction_count": 7
}
```

#### Courses (`/api/v1/courses/`)

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/courses/` | List / search courses (paginated) | Required |
| POST | `/courses/` | Create course | Admin |
| GET | `/courses/{id}/` | Course detail | Required |
| PUT | `/courses/{id}/` | Update course | Admin |
| DELETE | `/courses/{id}/` | Soft delete (set is_active=False) | Admin |
| POST | `/courses/{id}/syllabus/` | Upload syllabus PDF (triggers vectorization) | Admin |
| GET | `/courses/{id}/stats/` | Enrollment count, recommendation count | Admin |

**Query params for GET `/courses/`:** `search`, `department`, `level`, `credits`, `page`, `page_size`

**Course list item shape:**
```json
{
  "id": 42,
  "code": "IT801",
  "title": "Advanced Machine Learning",
  "description": "Covers deep learning, ensemble methods...",
  "credits": 3,
  "level": "postgraduate",
  "department": {"id": 1, "name": "Information Technology", "code": "IT"},
  "tags": ["machine learning", "neural networks", "python"],
  "prerequisite_ids": [15, 20],
  "is_active": true
}
```

#### Recommendations (`/api/v1/recommendations/`)

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/recommendations/` | Get current student's Top-N recommendations | Student |
| POST | `/recommendations/refresh/` | Force regenerate recommendations | Student |
| POST | `/recommendations/{id}/feedback/` | Submit thumbs up/down | Student |
| GET | `/recommendations/history/` | Past recommendations with feedback | Student |

**Recommendations response shape:**
```json
{
  "student_id": 1,
  "is_cold_start": false,
  "w_weight": 0.6,
  "generated_at": "2025-06-27T10:00:00Z",
  "recommendations": [
    {
      "id": 101,
      "rank": 1,
      "score": 0.923,
      "recommendation_type": "HYBRID",
      "rationale": "9 of 10 students with your profile enrolled in this course",
      "course": {
        "id": 42,
        "code": "IT801",
        "title": "Advanced Machine Learning",
        "credits": 3,
        "department": "Information Technology",
        "tags": ["machine learning", "neural networks"]
      }
    }
  ]
}
```

**Feedback request body:**
```json
{ "rating": 1, "comment": "Very relevant to my program" }
```
Rating: `1` = positive, `-1` = negative.

#### Admin — Analytics (`/api/v1/admin/`)

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/admin/analytics/` | Accuracy metrics + engagement stats | Admin |
| GET | `/admin/analytics/recommendations/` | Recommendation audit log (paginated) | Admin |
| GET | `/admin/settings/` | Get current engine settings | Admin |
| PUT | `/admin/settings/` | Update W, Top-N, cold-start threshold | Admin |
| POST | `/admin/engine/retrain/` | Trigger full model retrain via Celery | Admin |
| GET | `/admin/students/` | List all students with profile summary | Admin |

**Analytics response shape:**
```json
{
  "summary": {
    "total_students": 340,
    "active_students_30d": 112,
    "total_recommendations_generated": 5420,
    "positive_feedback_rate": 0.74,
    "average_click_through_rate": 0.41
  },
  "accuracy": {
    "mae": 0.31,
    "rmse": 0.48,
    "f1_score": 0.78,
    "precision": 0.81,
    "recall": 0.75
  },
  "top_recommended_courses": [
    {"course_id": 42, "title": "Advanced ML", "recommendation_count": 210}
  ]
}
```

---

### 5.4 Recommendation Engine

Place all engine logic in `backend/engine/` with no Django imports so it can be unit-tested independently.

#### `engine/content_based.py`
```python
"""
Content-Based Filtering using TF-IDF cosine similarity.
Takes student interests + completed course tags → finds similar courses.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict


def build_tfidf_matrix(course_texts: List[str]) -> tuple:
    """
    Build TF-IDF matrix from course description/syllabus texts.
    Returns (matrix, vectorizer) so vectorizer can be reused for query vectors.
    """
    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1,
    )
    matrix = vectorizer.fit_transform(course_texts)
    return matrix, vectorizer


def build_student_query_vector(interests: List[str], vectorizer: TfidfVectorizer) -> np.ndarray:
    """
    Convert student interests list into a TF-IDF query vector.
    Joins interests into a single text document.
    """
    query_text = ' '.join(interests)
    return vectorizer.transform([query_text])


def compute_cbf_scores(
    student_interests: List[str],
    courses: List[Dict],
    exclude_course_ids: List[int],
) -> List[Dict]:
    """
    Compute content-based scores for each course.

    Args:
        student_interests: list of interest strings from student profile
        courses: list of dicts with keys: id, combined_text (description + syllabus + tags joined)
        exclude_course_ids: course IDs the student has already completed

    Returns:
        List of {course_id, cbf_score} sorted descending by score
    """
    if not courses or not student_interests:
        return []

    course_texts = [c['combined_text'] for c in courses]
    matrix, vectorizer = build_tfidf_matrix(course_texts)
    query_vector = build_student_query_vector(student_interests, vectorizer)

    similarities = cosine_similarity(query_vector, matrix).flatten()

    results = []
    for i, course in enumerate(courses):
        if course['id'] in exclude_course_ids:
            continue
        results.append({
            'course_id': course['id'],
            'cbf_score': float(similarities[i]),
        })

    return sorted(results, key=lambda x: x['cbf_score'], reverse=True)
```

#### `engine/collaborative.py`
```python
"""
Collaborative Filtering using SVD matrix factorization.
Finds latent patterns in student-course enrollment history.
"""
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from typing import List, Dict, Optional


def build_interaction_matrix(interactions: List[Dict]) -> tuple:
    """
    Build student-course interaction matrix from interaction logs.

    Args:
        interactions: list of {student_id, course_id, implicit_score}
                     implicit_score = normalized(clicks * 0.3 + time_spent_norm * 0.7)

    Returns:
        (matrix as DataFrame, student_ids list, course_ids list)
    """
    df = pd.DataFrame(interactions)
    if df.empty:
        return None, [], []

    pivot = df.pivot_table(
        index='student_id',
        columns='course_id',
        values='implicit_score',
        fill_value=0,
    )
    return pivot, list(pivot.index), list(pivot.columns)


def compute_svd_predictions(interaction_df: pd.DataFrame, n_factors: int = 20) -> pd.DataFrame:
    """
    Apply SVD to the interaction matrix and return full predicted ratings matrix.
    """
    matrix = csr_matrix(interaction_df.values)
    # Number of factors capped at min(rows, cols) - 1
    k = min(n_factors, min(matrix.shape) - 1)
    U, sigma, Vt = svds(matrix, k=k)

    # Reconstruct the full matrix
    sigma_diag = np.diag(sigma)
    predicted = np.dot(np.dot(U, sigma_diag), Vt)
    return pd.DataFrame(predicted, index=interaction_df.index, columns=interaction_df.columns)


def get_cf_scores_for_student(
    student_id: int,
    predicted_df: pd.DataFrame,
    exclude_course_ids: List[int],
) -> List[Dict]:
    """
    Extract CF scores for a specific student from the predicted matrix.
    Excludes courses the student has already completed.
    """
    if student_id not in predicted_df.index:
        return []

    student_row = predicted_df.loc[student_id]
    results = []

    for course_id, score in student_row.items():
        if course_id in exclude_course_ids:
            continue
        results.append({
            'course_id': int(course_id),
            'cf_score': float(score),
        })

    return sorted(results, key=lambda x: x['cf_score'], reverse=True)
```

#### `engine/hybrid.py`
```python
"""
Hybrid engine — blends CF and CBF scores using weight W.
"""
from typing import List, Dict


def normalize_scores(scores: List[Dict], score_key: str) -> List[Dict]:
    """Min-max normalize scores to [0, 1] range."""
    if not scores:
        return scores
    values = [s[score_key] for s in scores]
    min_val, max_val = min(values), max(values)
    if max_val == min_val:
        for s in scores:
            s[f'{score_key}_norm'] = 1.0
    else:
        for s in scores:
            s[f'{score_key}_norm'] = (s[score_key] - min_val) / (max_val - min_val)
    return scores


def blend_scores(
    cf_scores: List[Dict],
    cbf_scores: List[Dict],
    w: float,
    top_n: int = 5,
) -> List[Dict]:
    """
    Blend CF and CBF scores using the hybrid formula:
        S_hybrid = W * S_cf + (1 - W) * S_cbf

    Args:
        cf_scores: list of {course_id, cf_score}
        cbf_scores: list of {course_id, cbf_score}
        w: hybrid weight (0.0 = pure CBF, 1.0 = pure CF)
        top_n: number of results to return

    Returns:
        Top-N results as list of {course_id, hybrid_score, cf_score, cbf_score, recommendation_type}
    """
    # Normalize both score sets
    cf_scores = normalize_scores(cf_scores, 'cf_score')
    cbf_scores = normalize_scores(cbf_scores, 'cbf_score')

    # Build lookup dicts
    cf_map = {s['course_id']: s.get('cf_score_norm', 0.0) for s in cf_scores}
    cbf_map = {s['course_id']: s.get('cbf_score_norm', 0.0) for s in cbf_scores}

    all_course_ids = set(cf_map.keys()) | set(cbf_map.keys())

    results = []
    for course_id in all_course_ids:
        cf = cf_map.get(course_id, 0.0)
        cbf = cbf_map.get(course_id, 0.0)
        hybrid = w * cf + (1 - w) * cbf

        # Determine recommendation type label
        if w == 0.0 or cf == 0.0:
            rec_type = 'CBF'
        elif cbf == 0.0:
            rec_type = 'CF'
        else:
            rec_type = 'HYBRID'

        results.append({
            'course_id': course_id,
            'hybrid_score': hybrid,
            'cf_score': cf,
            'cbf_score': cbf,
            'recommendation_type': rec_type,
        })

    results.sort(key=lambda x: x['hybrid_score'], reverse=True)
    return results[:top_n]


def generate_rationale(rec: Dict, peer_count: int = None) -> str:
    """
    Generate a human-readable rationale string for a recommendation.
    """
    if rec['recommendation_type'] == 'CBF':
        return "Matches your stated academic interests"
    elif rec['recommendation_type'] == 'CF' and peer_count:
        return f"{peer_count} students with your profile enrolled in this course"
    elif rec['recommendation_type'] == 'HYBRID':
        return f"Strong match for your interests and popular with similar students"
    return "Recommended based on your profile"
```

#### `engine/utils.py`
```python
"""Shared utilities for the recommendation engine."""
import numpy as np


def compute_implicit_score(clicks: int, time_spent_seconds: int) -> float:
    """
    Convert raw interaction signals to a single implicit preference score.
    Weights: clicks 30%, normalized time 70%.
    """
    # Normalize time to 0-1 using 30 minutes as max
    time_norm = min(time_spent_seconds / 1800, 1.0)
    click_norm = min(clicks / 50, 1.0)  # 50 clicks as max
    return round(0.3 * click_norm + 0.7 * time_norm, 4)


def compute_mae(actual: list, predicted: list) -> float:
    actual_arr = np.array(actual)
    predicted_arr = np.array(predicted)
    return float(np.mean(np.abs(actual_arr - predicted_arr)))


def compute_rmse(actual: list, predicted: list) -> float:
    actual_arr = np.array(actual)
    predicted_arr = np.array(predicted)
    return float(np.sqrt(np.mean((actual_arr - predicted_arr) ** 2)))
```

---

### 5.5 Authentication

Use `djangorestframework-simplejwt`. Create a custom login view that returns user info alongside tokens:

```python
# apps/users/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'onboarding_complete': getattr(user, 'student_profile', None) and user.student_profile.onboarding_complete,
        }
        return data

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
```

---

### 5.6 Celery Tasks

```python
# tasks/recommendation.py
from celery import shared_task
from apps.users.models import User
from apps.interactions.models import Interaction, Enrollment
from apps.courses.models import Course
from apps.recommendations.models import RecommendationResult, EngineSettings
from engine.hybrid import blend_scores, generate_rationale
from engine.collaborative import build_interaction_matrix, compute_svd_predictions, get_cf_scores_for_student
from engine.content_based import compute_cbf_scores
from engine.utils import compute_implicit_score


@shared_task(bind=True, max_retries=3)
def generate_recommendations_for_student(self, student_id: int):
    """
    Generate and persist Top-N recommendations for a single student.
    Called when: student refreshes, student updates profile, or admin triggers retrain.
    """
    try:
        settings = EngineSettings.get_settings()
        student = User.objects.select_related('student_profile').get(id=student_id)
        profile = student.student_profile

        # Get interaction count to check cold-start
        interaction_count = Interaction.objects.filter(student=student).count()
        is_cold_start = interaction_count < settings.cold_start_threshold

        completed_ids = profile.completed_course_ids or []
        active_courses = list(Course.objects.filter(is_active=True).values(
            'id', 'description', 'syllabus_text', 'tags'
        ))

        # Build combined text for CBF
        for course in active_courses:
            tags_text = ' '.join(course.get('tags') or [])
            course['combined_text'] = f"{course['description']} {course['syllabus_text']} {tags_text}"

        w = 0.0 if is_cold_start else settings.hybrid_weight

        # CBF scores — always computed
        cbf_scores = compute_cbf_scores(
            student_interests=profile.interests or [],
            courses=active_courses,
            exclude_course_ids=completed_ids,
        )

        cf_scores = []
        if not is_cold_start:
            # Build interaction matrix from all students
            interactions_qs = Interaction.objects.all().values('student_id', 'course_id', 'clicks', 'time_spent_seconds')
            interactions_for_engine = [
                {
                    'student_id': i['student_id'],
                    'course_id': i['course_id'],
                    'implicit_score': compute_implicit_score(i['clicks'], i['time_spent_seconds']),
                }
                for i in interactions_qs
            ]
            interaction_df, _, _ = build_interaction_matrix(interactions_for_engine)
            if interaction_df is not None:
                predicted_df = compute_svd_predictions(interaction_df)
                cf_scores = get_cf_scores_for_student(student_id, predicted_df, completed_ids)

        # Blend
        results = blend_scores(cf_scores, cbf_scores, w=w, top_n=settings.top_n)

        # Persist — delete old and write new
        RecommendationResult.objects.filter(student=student).delete()
        for rank, rec in enumerate(results, start=1):
            RecommendationResult.objects.create(
                student=student,
                course_id=rec['course_id'],
                score=rec['hybrid_score'],
                rank=rank,
                recommendation_type=rec['recommendation_type'],
                w_weight=w,
            )

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task
def retrain_all_students():
    """Bulk retrain for all active students. Triggered by admin or nightly schedule."""
    student_ids = User.objects.filter(role='student', is_active=True).values_list('id', flat=True)
    for student_id in student_ids:
        generate_recommendations_for_student.delay(student_id)
```

---

## 6. Frontend — Next.js

### 6.1 Project Bootstrap

```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd frontend

# Install dependencies
npm install zustand @tanstack/react-query axios react-hook-form zod @hookform/resolvers
npm install recharts date-fns clsx tailwind-merge lucide-react
npm install next-auth@beta

# shadcn/ui
npx shadcn-ui@latest init
# Choose: Default style, Zinc base color, CSS variables = yes
# Add components:
npx shadcn-ui@latest add button card badge input label textarea select dialog toast progress tabs avatar dropdown-menu sheet skeleton separator
```

---

### 6.2 Directory Structure

```
frontend/src/
├── app/
│   ├── layout.tsx                      # Root layout: fonts, providers
│   ├── globals.css
│   ├── (auth)/
│   │   ├── layout.tsx                  # Auth layout: centered card, no nav
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       ├── page.tsx                # Step 1: account details
│   │       └── onboarding/
│   │           └── page.tsx            # Step 2: interests selection
│   ├── (student)/
│   │   ├── layout.tsx                  # Student layout: sidebar nav + header
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── catalog/
│   │   │   ├── page.tsx                # Course list with search + filters
│   │   │   └── [id]/
│   │   │       └── page.tsx            # Course detail (SSR)
│   │   └── profile/
│   │       └── page.tsx
│   └── (admin)/
│       ├── layout.tsx                  # Admin layout: wider sidebar
│       ├── courses/
│       │   └── page.tsx
│       ├── analytics/
│       │   └── page.tsx
│       └── settings/
│           └── page.tsx
│
├── components/
│   ├── ui/                             # shadcn auto-generated — do not hand-edit
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── InterestPicker.tsx          # Tag cloud for onboarding
│   ├── recommendations/
│   │   ├── RecommendationCard.tsx
│   │   ├── RecommendationList.tsx
│   │   ├── FeedbackButtons.tsx
│   │   └── ColdStartBanner.tsx
│   ├── courses/
│   │   ├── CourseCard.tsx
│   │   ├── CourseGrid.tsx
│   │   ├── CourseFilters.tsx
│   │   └── SyllabusUpload.tsx
│   ├── admin/
│   │   ├── CourseTable.tsx
│   │   ├── EngineSettingsForm.tsx
│   │   ├── AnalyticsDashboard.tsx
│   │   └── MetricCard.tsx
│   └── shared/
│       ├── AppLayout.tsx
│       ├── Sidebar.tsx
│       ├── Header.tsx
│       ├── LoadingSpinner.tsx
│       ├── EmptyState.tsx
│       └── ProtectedRoute.tsx
│
├── lib/
│   ├── api.ts                          # Axios instance + typed request functions
│   ├── auth.ts                         # NextAuth config
│   ├── schemas.ts                      # Zod validation schemas
│   └── utils.ts                        # clsx helpers, formatters
│
├── hooks/
│   ├── useRecommendations.ts
│   ├── useCourses.ts
│   ├── useProfile.ts
│   └── useAnalytics.ts
│
├── store/
│   ├── authStore.ts                    # User session state
│   └── uiStore.ts                      # Sidebar open/close, toast queue
│
└── types/
    └── index.ts                        # All shared TypeScript interfaces
```

---

### 6.3 Global Config

#### `src/lib/api.ts`
```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { getSession } from 'next-auth/react';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL!;

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

// Attach JWT token to every request
api.interceptors.request.use(async (config) => {
  const session = await getSession();
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`;
  }
  return config;
});

// Auto-refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      // Trigger NextAuth session refresh
      const event = new Event('visibilitychange');
      document.dispatchEvent(event);
    }
    return Promise.reject(error);
  }
);

export default api;

// Typed API functions
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login/', { email, password }),
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post('/auth/register/', data),
  refresh: (refresh: string) =>
    api.post('/auth/refresh/', { refresh }),
  logout: (refresh: string) =>
    api.post('/auth/logout/', { refresh }),
};

export const recommendationsApi = {
  getRecommendations: () =>
    api.get('/recommendations/'),
  refresh: () =>
    api.post('/recommendations/refresh/'),
  submitFeedback: (id: number, rating: 1 | -1, comment?: string) =>
    api.post(`/recommendations/${id}/feedback/`, { rating, comment }),
};

export const coursesApi = {
  list: (params?: Record<string, unknown>) =>
    api.get('/courses/', { params }),
  get: (id: number) =>
    api.get(`/courses/${id}/`),
  create: (data: unknown) =>
    api.post('/courses/', data),
  update: (id: number, data: unknown) =>
    api.put(`/courses/${id}/`, data),
  uploadSyllabus: (id: number, file: File) => {
    const form = new FormData();
    form.append('syllabus', file);
    return api.post(`/courses/${id}/syllabus/`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const studentApi = {
  getProfile: () => api.get('/students/me/'),
  updateProfile: (data: unknown) => api.put('/students/me/', data),
};

export const adminApi = {
  getAnalytics: () => api.get('/admin/analytics/'),
  getSettings: () => api.get('/admin/settings/'),
  updateSettings: (data: unknown) => api.put('/admin/settings/', data),
  retrain: () => api.post('/admin/engine/retrain/'),
};
```

#### `src/types/index.ts`
```typescript
export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'student' | 'admin';
  onboarding_complete: boolean;
}

export interface StudentProfile extends User {
  program: string;
  level: string;
  interests: string[];
  gpa: string | null;
  completed_course_ids: number[];
  interaction_count: number;
}

export interface Department {
  id: number;
  name: string;
  code: string;
}

export interface Course {
  id: number;
  code: string;
  title: string;
  description: string;
  credits: number;
  level: string;
  department: Department;
  tags: string[];
  prerequisite_ids: number[];
  is_active: boolean;
}

export type RecommendationType = 'CF' | 'CBF' | 'HYBRID';

export interface Recommendation {
  id: number;
  rank: number;
  score: number;
  recommendation_type: RecommendationType;
  rationale: string;
  course: Pick<Course, 'id' | 'code' | 'title' | 'credits' | 'tags'> & { department: string };
  feedback?: { rating: 1 | -1 } | null;
}

export interface RecommendationsResponse {
  student_id: number;
  is_cold_start: boolean;
  w_weight: number;
  generated_at: string;
  recommendations: Recommendation[];
}

export interface EngineSettings {
  hybrid_weight: number;
  top_n: number;
  cold_start_threshold: number;
  updated_at: string;
}

export interface AnalyticsData {
  summary: {
    total_students: number;
    active_students_30d: number;
    total_recommendations_generated: number;
    positive_feedback_rate: number;
    average_click_through_rate: number;
  };
  accuracy: {
    mae: number;
    rmse: number;
    f1_score: number;
    precision: number;
    recall: number;
  };
  top_recommended_courses: Array<{
    course_id: number;
    title: string;
    recommendation_count: number;
  }>;
}
```

#### `src/lib/schemas.ts`
```typescript
import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export const registerSchema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
}).refine((data) => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

export const onboardingSchema = z.object({
  program: z.string().min(2, 'Enter your program name'),
  level: z.enum(['undergraduate', 'postgraduate']),
  interests: z.array(z.string()).min(1, 'Select at least one interest'),
});

export const courseSchema = z.object({
  code: z.string().min(2).max(20),
  title: z.string().min(3).max(255),
  description: z.string().min(20),
  credits: z.number().int().min(1).max(10),
  department_id: z.number().int().positive(),
  level: z.string().min(1),
  tags: z.array(z.string()).default([]),
});

export const engineSettingsSchema = z.object({
  hybrid_weight: z.number().min(0).max(1),
  top_n: z.number().int().min(1).max(20),
  cold_start_threshold: z.number().int().min(1).max(20),
});
```

---

### 6.4 Pages & Routes

#### `src/app/(student)/dashboard/page.tsx`

This is the main page. It must:
1. Call `GET /recommendations/` on mount via React Query
2. Display `<RecommendationList>` when data is ready
3. Show `<ColdStartBanner>` when `is_cold_start === true`
4. Show a `<LoadingSpinner>` skeleton (5 cards) while loading
5. Include a "Refresh recommendations" button that calls `POST /recommendations/refresh/` then invalidates the query cache
6. Show `generated_at` timestamp in top-right corner ("Last updated 2 hours ago")

```typescript
// Key implementation notes:
// - Use React Query: const { data, isLoading, refetch } = useQuery({ queryKey: ['recommendations'], queryFn: fetchRecommendations })
// - Cache time: 5 minutes (staleTime: 5 * 60 * 1000)
// - The refresh button should show a loading spinner while the Celery task runs (poll every 2s for up to 30s)
```

#### `src/app/(student)/catalog/page.tsx`

Course browser with:
- Search input (debounced 300ms) → updates `search` query param → triggers API call
- Filter sidebar: department (dropdown), level (radio), credits (slider 1–6)
- Paginated grid of `<CourseCard>` components (20 per page)
- URL-driven state: all filter values reflected in URL search params so the page is shareable

#### `src/app/(student)/catalog/[id]/page.tsx`

Server-rendered course detail page:
- `generateStaticParams` is NOT used (courses change frequently) — use `dynamic = 'force-dynamic'`
- Fetch course data server-side with `fetch()` using the internal API URL
- Show: title, code, credits, department, description, prerequisites list, tags, syllabus excerpt (first 300 chars)
- "Add to wishlist" button (store in local Zustand state for v1)

#### `src/app/(student)/profile/page.tsx`

Two-section page:
1. **Academic info** — program, level, GPA (editable form, PUT to `/students/me/`)
2. **Interests** — reuse `<InterestPicker>` component; on save, trigger recommendation refresh

#### `src/app/(admin)/courses/page.tsx`

Full-featured data table:
- Use shadcn `<DataTable>` pattern with TanStack Table
- Columns: Code, Title, Department, Credits, Status (Active/Inactive), Actions
- Actions per row: Edit (opens Dialog), Upload Syllabus (opens Sheet/drawer), Deactivate
- "Add Course" button → opens Dialog with `<CourseForm>` using `courseSchema`
- Inline search by title or code

#### `src/app/(admin)/analytics/page.tsx`

Dashboard with:
- 5 metric cards: Total Students, Active 30d, Recommendations Generated, Positive Feedback Rate, Click-Through Rate
- Two Recharts charts: LineChart (MAE/RMSE over time — mock data for v1), BarChart (top 10 recommended courses)
- Accuracy metrics: MAE, RMSE, F1, Precision, Recall shown as stat cards

#### `src/app/(admin)/settings/page.tsx`

Form using `engineSettingsSchema`:
- `hybrid_weight`: slider input with value display (0.00 – 1.00, step 0.05)
- `top_n`: number input (1–20)
- `cold_start_threshold`: number input (1–20)
- Save button → PUT `/admin/settings/`
- "Re-train Model" button → POST `/admin/engine/retrain/` → show success toast

---

### 6.5 Components

#### `src/components/recommendations/RecommendationCard.tsx`

Props: `recommendation: Recommendation`, `onFeedback: (id: number, rating: 1 | -1) => void`

Visual layout:
- Top-left: rank badge (e.g. "#1") in `bg-primary text-primary-foreground`
- Top-right: `RecommendationType` badge — HYBRID (purple), CF (blue), CBF (teal)
- Course code in muted text, title in bold large text
- Credits badge and department name
- Relevance score as a `<Progress>` bar (score × 100)
- Rationale text in italic muted style
- Bottom: thumbs up / thumbs down buttons — grey by default, green/red after click
- If `feedback` is already set, show the chosen state and disable both buttons

#### `src/components/recommendations/ColdStartBanner.tsx`

Informational banner shown when `is_cold_start === true`:
```
ℹ️  You're seeing interest-based suggestions. Complete more courses or update your 
    profile to unlock peer-based recommendations.
```
Style: blue info banner, dismissable with an X.

#### `src/components/auth/InterestPicker.tsx`

Props: `value: string[]`, `onChange: (interests: string[]) => void`

A tag-cloud of predefined interest areas. Clicking a tag toggles it selected (filled) or unselected (outlined). Selected tags shown in primary color. At least 1 required (enforced by Zod schema).

Predefined interests:
```
Machine Learning, Deep Learning, Databases, Networking, Cloud Computing,
Cybersecurity, Data Science, Software Engineering, Mobile Development,
Web Development, Computer Vision, Natural Language Processing,
Algorithms, Operating Systems, Distributed Systems, DevOps
```

#### `src/components/admin/EngineSettingsForm.tsx`

```typescript
// Key implementation: hybrid_weight uses a range input styled with Tailwind
// Show live preview text: "W = 0.6 → 60% peer behavior, 40% course content"
// Update preview text reactively as slider moves
```

---

### 6.6 State Management

#### `src/store/authStore.ts`
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  setUser: (user: User, token: string) => void;
  clearUser: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      setUser: (user, accessToken) => set({ user, accessToken }),
      clearUser: () => set({ user: null, accessToken: null }),
    }),
    { name: 'auth-storage' }
  )
);
```

#### `src/hooks/useRecommendations.ts`
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { recommendationsApi } from '@/lib/api';
import { RecommendationsResponse } from '@/types';

export function useRecommendations() {
  const queryClient = useQueryClient();

  const query = useQuery<RecommendationsResponse>({
    queryKey: ['recommendations'],
    queryFn: () => recommendationsApi.getRecommendations().then((r) => r.data),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const refreshMutation = useMutation({
    mutationFn: () => recommendationsApi.refresh().then((r) => r.data),
    onSuccess: () => {
      // Poll for updated results after Celery task runs
      setTimeout(() => queryClient.invalidateQueries({ queryKey: ['recommendations'] }), 3000);
    },
  });

  const feedbackMutation = useMutation({
    mutationFn: ({ id, rating }: { id: number; rating: 1 | -1 }) =>
      recommendationsApi.submitFeedback(id, rating).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });

  return { query, refreshMutation, feedbackMutation };
}
```

---

### 6.7 API Client

All API calls go through `src/lib/api.ts`. The frontend **never** calls the Django API directly from server components — Next.js API routes are used as a proxy for operations that need server-side token handling.

> **`API_URL` vs `NEXT_PUBLIC_API_URL`:** Both point to `http://localhost:8000/api/v1` in development because Next.js runs on the host alongside Docker. In production, both point to the live backend domain. There is no Docker-internal hostname (`http://backend:8000`) needed since the frontend is not inside Docker.

**Route handler for recommendations (server-side proxy):**
`src/app/api/recommendations/route.ts`
```typescript
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

export async function GET(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  // API_URL = http://localhost:8000/api/v1 (dev) or https://api.yourdomain.com/api/v1 (prod)
  const res = await fetch(`${process.env.API_URL}/recommendations/`, {
    headers: { Authorization: `Bearer ${session.accessToken}` },
  });

  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
```

---

## 7. Data Contracts (Shared Types)

These are the canonical shapes. Both Django serializers and TypeScript types must match exactly.

### Error Response (all endpoints)
```json
{
  "error": "string",
  "detail": "string or object with field errors",
  "code": "string"
}
```

### Pagination Wrapper (list endpoints)
```json
{
  "count": 100,
  "next": "http://api/courses/?page=2",
  "previous": null,
  "results": []
}
```

### Token Expiry Handling
- Access token: 15 minutes
- Refresh token: 7 days
- Frontend must catch `401` responses and call `/auth/refresh/` automatically using the Axios interceptor
- On refresh failure, clear session and redirect to `/login`

---

## 8. Recommendation Engine Logic

### When recommendations are generated

| Trigger | Who | Mechanism |
|---|---|---|
| Student first login (after onboarding) | System | Signal from `StudentProfile.post_save` |
| Student clicks "Refresh" | Student | `POST /recommendations/refresh/` → Celery |
| Student updates profile/interests | Student | Signal from `StudentProfile.post_save` |
| Admin triggers retrain | Admin | `POST /admin/engine/retrain/` → Celery bulk |
| Nightly retrain (all students) | System | Celery beat schedule: 02:00 UTC daily |

### Cold-start detection

```python
# In the recommendation view and Celery task:
interaction_count = Interaction.objects.filter(student=student).count()
is_cold_start = interaction_count < settings.cold_start_threshold  # default: 3

if is_cold_start:
    w = 0.0  # Pure CBF
else:
    w = settings.hybrid_weight  # Admin-configured value
```

### Syllabus vectorization (triggered on upload)

```python
# In apps/courses/views.py after saving the uploaded file:
from sklearn.feature_extraction.text import TfidfVectorizer
import PyPDF2  # or pdfplumber

def extract_text_from_pdf(file) -> str:
    # Extract and return text from PDF
    ...

def vectorize_course(course: Course):
    """
    Re-vectorize a course's TF-IDF vector after syllabus upload.
    Uses the same vocabulary as the global vectorizer.
    Store the result in course.syllabus_vector as a JSON list.
    """
    # In production: fit vectorizer on all courses, then transform
    # For v1: store raw text in syllabus_text and compute vectors at recommendation time
    combined = f"{course.description} {course.syllabus_text} {' '.join(course.tags)}"
    course.syllabus_text = extract_text_from_pdf(course.syllabus_file)
    course.save(update_fields=['syllabus_text', 'syllabus_file'])
```

---

## 9. Testing Requirements

### Backend

```bash
# Run all tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report --min-coverage=80
```

**Required test cases:**

`apps/users/tests.py`:
- `test_register_creates_user_and_profile`
- `test_login_returns_tokens`
- `test_login_invalid_credentials_returns_401`
- `test_duplicate_email_registration_fails`

`apps/recommendations/tests.py`:
- `test_cold_start_uses_cbf_only`
- `test_recommendations_exclude_completed_courses`
- `test_hybrid_blend_respects_weight`
- `test_refresh_endpoint_triggers_celery_task`

`engine/tests.py`:
- `test_cbf_scores_ranked_correctly`
- `test_normalize_scores_range`
- `test_blend_scores_formula`
- `test_cold_start_w_equals_zero`

### Frontend

```bash
# Unit + integration
npm test

# E2E
npx playwright test
```

**Required Playwright test flows (`tests/e2e/`):**

`auth.spec.ts`:
- Student can register, complete onboarding, and land on dashboard
- Invalid credentials show error message
- Logged-out user redirected from `/dashboard` to `/login`

`recommendations.spec.ts`:
- Dashboard shows 5 recommendation cards after login
- Clicking thumbs up changes button state and shows success toast
- Clicking "Refresh" shows loading state then updates cards

`admin.spec.ts`:
- Admin can create a course and see it in the table
- Admin can update W weight in settings and see confirmation
- Analytics page renders all metric cards

---

## 10. Docker & Deployment

### Architecture Overview

The **backend stack** (Django, PostgreSQL, Redis, Celery) runs in Docker. The **frontend** (Next.js) runs directly on the host machine with `npm run dev`. This means:

- Faster frontend iteration — no rebuild step, instant HMR
- No Docker knowledge required to work on the frontend
- Backend port `8000` is exposed to the host so the frontend can reach it at `http://localhost:8000`

```
┌─────────────────────────────────────────────┐
│  Your Machine (host)                        │
│                                             │
│   npm run dev → Next.js :3000               │
│        │                                    │
│        │ http://localhost:8000/api/v1        │
│        ▼                                    │
│  ┌──────────────────────────────────────┐   │
│  │  Docker Compose                      │   │
│  │                                      │   │
│  │  backend (Django)  :8000             │   │
│  │  db (PostgreSQL)   :5432             │   │
│  │  redis             :6379             │   │
│  │  celery worker                       │   │
│  │  celery beat                         │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

### `docker-compose.yml` (backend only — development)

```yaml
version: '3.9'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: escrs_db
      POSTGRES_USER: escrs_user
      POSTGRES_PASSWORD: escrs_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"   # Exposed so you can inspect the DB locally with psql or TablePlus

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"   # Exposed for local debugging with redis-cli

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app   # Live reload — code changes apply without rebuilding
    ports:
      - "8000:8000"   # Exposed to host so the local Next.js dev server can reach it
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development
      - DATABASE_URL=postgresql://escrs_user:escrs_pass@db:5432/escrs_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery:
    build: ./backend
    command: celery -A config worker -l info
    volumes:
      - ./backend:/app
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development
      - DATABASE_URL=postgresql://escrs_user:escrs_pass@db:5432/escrs_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery-beat:
    build: ./backend
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - ./backend:/app
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development
      - DATABASE_URL=postgresql://escrs_user:escrs_pass@db:5432/escrs_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

> **No frontend service.** The frontend is intentionally absent from Docker Compose. Do not add it.

---

### Starting the full dev environment

**Terminal 1 — start backend infrastructure:**
```bash
cd escrs/
docker compose up --build
```

Wait for `Starting development server at http://0.0.0.0:8000/` in the logs before starting the frontend.

**Terminal 2 — start frontend locally:**
```bash
cd escrs/frontend/
cp .env.example .env.local    # first time only — fill in NEXTAUTH_SECRET
npm install                   # first time only
npm run dev
```

App is now running at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api/v1`
- Django admin: `http://localhost:8000/admin`

---

### CORS configuration

Because the frontend (`localhost:3000`) and backend (`localhost:8000`) run on different ports, CORS must be configured in Django. In `config/settings/development.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Allow cookies/auth headers to be sent cross-origin
CORS_ALLOW_CREDENTIALS = True
```

---

### `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
```

> **No `frontend/Dockerfile`** — the frontend does not run in Docker. Do not create one.

---

### Frontend — local prerequisites

The developer's machine needs:

| Tool | Version | Install |
|---|---|---|
| Node.js | 20 LTS+ | `https://nodejs.org` or `nvm install 20` |
| npm | 10+ | Bundled with Node |
| Docker Desktop | latest | `https://docker.com` |

No global CLI tools beyond Node and Docker are required.

---

### Production deployment note

In production, the frontend can be deployed independently to **Vercel** (recommended for Next.js) or any static/SSR host. The backend Docker stack deploys to any VPS, ECS, or Kubernetes environment. Update `NEXT_PUBLIC_API_URL` and `API_URL` in the production environment to point to the live backend URL.

```env
# Production frontend env (set in Vercel dashboard or host provider)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
API_URL=https://api.yourdomain.com/api/v1
NEXTAUTH_URL=https://yourdomain.com
NEXTAUTH_SECRET=<strong-random-secret>
```

---

## 11. Implementation Order

Follow this exact order to avoid blocked dependencies:

### Phase 1 — Backend Foundation (Days 1–4)
1. Set up Django project structure and settings; bring up backend-only Docker Compose (`db`, `redis`, `backend`, `celery`, `celery-beat`)
2. Implement `User` and `StudentProfile` models + migrations
3. Implement JWT auth endpoints (register, login, refresh, logout)
4. Implement `Department` and `Course` models
5. Implement `Interaction`, `Enrollment` models
6. Implement `RecommendationResult`, `Feedback`, `EngineSettings` models
7. Run migrations, create superuser, seed with sample data

### Phase 2 — Recommendation Engine (Days 5–7)
1. Implement `engine/utils.py`
2. Implement `engine/content_based.py` with unit tests
3. Implement `engine/collaborative.py` with unit tests
4. Implement `engine/hybrid.py` with unit tests
5. Wire engine into `tasks/recommendation.py` Celery task
6. Implement `GET /recommendations/` and `POST /recommendations/refresh/` views

### Phase 3 — Remaining Backend APIs (Days 8–10)
1. Course CRUD endpoints + syllabus upload
2. Student profile endpoints
3. Feedback endpoint
4. Admin analytics endpoint
5. Admin settings endpoint
6. Generate OpenAPI schema: `python manage.py spectacular --file schema.yml`

### Phase 4 — Frontend Foundation (Days 11–13)
1. Bootstrap Next.js locally (`npx create-next-app@latest`), install all dependencies, configure shadcn — **do not add to Docker Compose**
2. Confirm backend is running via Docker (`docker compose up`) and `http://localhost:8000/api/v1` is reachable from host
3. Set up `src/types/index.ts`, `src/lib/api.ts`, `src/lib/schemas.ts`
4. Set up NextAuth with JWT backend; verify CORS headers on Django allow `localhost:3000`
5. Implement auth pages: Login, Register, Onboarding
6. Implement root layouts and protected route logic

### Phase 5 — Student-Facing Features (Days 14–17)
1. Build `<RecommendationCard>`, `<RecommendationList>`, `<ColdStartBanner>`
2. Build student dashboard page
3. Build course catalog page with search and filters
4. Build course detail page (SSR)
5. Build student profile page with `<InterestPicker>`

### Phase 6 — Admin Portal (Days 18–20)
1. Build `<CourseTable>` with CRUD dialogs
2. Build admin courses page
3. Build `<AnalyticsDashboard>` with Recharts charts
4. Build admin analytics page
5. Build engine settings page

### Phase 7 — Testing & QA (Days 21–24)
1. Backend unit tests (engine + API views)
2. Frontend component tests (React Testing Library)
3. Playwright E2E test suite
4. Fix failures, hit 80% coverage threshold

### Phase 8 — Deployment (Days 25–26)
1. **Backend:** Add Nginx reverse proxy to `docker-compose.prod.yml`; run `python manage.py check --deploy`; deploy backend Docker stack to VPS or cloud (ECS / DigitalOcean / Railway)
2. **Frontend:** Deploy to Vercel (`vercel deploy`) — set `NEXT_PUBLIC_API_URL`, `API_URL`, `NEXTAUTH_URL`, and `NEXTAUTH_SECRET` in Vercel environment variables dashboard
3. Update Django `CORS_ALLOWED_ORIGINS` and `ALLOWED_HOSTS` in production settings to include the live Vercel domain
4. End-to-end smoke test all critical flows against production URLs

---

*End of ESCRS Build Specification v1.0*
*Author: Idahosa Joshua — MIT, Miva Open University*
