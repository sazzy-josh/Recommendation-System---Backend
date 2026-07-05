from .base import *

DEBUG = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Run Celery tasks synchronously — no Redis/broker required in dev
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Drop django_celery_beat when running without a broker
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django_celery_beat']
