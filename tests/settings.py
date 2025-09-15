import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'test-secret-key'

DEBUG = True

INSTALLED_APPS = [
    'django_otel',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MIDDLEWARE = [
    'django_otel.middleware.OpenTelemetryMiddleware',
]

OTEL_EXPORTER_OTLP_ENDPOINT = 'http://localhost:4317'
OTEL_ENABLED = True