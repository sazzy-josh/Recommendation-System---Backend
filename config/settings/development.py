from .base import *

DEBUG = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Docker Compose runs a real broker (Redis) plus celery worker/beat services,
# so tasks are queued by default. Set CELERY_TASK_ALWAYS_EAGER=True in .env to
# run tasks synchronously when working outside Docker without Redis.
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', default=False)
CELERY_TASK_EAGER_PROPAGATES = True

if CELERY_TASK_ALWAYS_EAGER:
    # Drop django_celery_beat when running without a broker
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django_celery_beat']
