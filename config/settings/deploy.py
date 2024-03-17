from .base import *

def read_secret(secret_name):
    file = open("/run/secrets/" + secret_name)
    secret = file.read()
    secret = secret.rstrip().lstrip()
    file.close()
    return secret

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = read_secret("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": read_secret("POSTGRES_DB"),
        "USER": read_secret("POSTGRES_USER"),
        "PASSWORD": read_secret("POSTGRES_PASSWORD"),
        "HOST": "postgresdb",
        "PORT": "5432",
    }
}

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': '',
    },
} 

SOCIALACCOUNT_PROVIDERS = {
    'naver': {'APP': {
                        'client_id': read_secret("NAVER_CLIENT_ID"),
                        'secret': read_secret("NAVER_CLIENT_SECRET"),
                        'key': ''
                }},
    'google': {'APP': {
                        'client_id': read_secret("GOOGLE_CLIENT_ID"),
                        'secret': read_secret("GOOGLE_CLIENT_SECRET"),
                        'key': ''
                }},
    'kakao': {'APP': {
                        'client_id': read_secret("KAKAO_CLIENT_ID"),
                        'secret': read_secret("KAKAO_CLIENT_SECRET"),
                        'key': ''
                }},
}

CSRF_TRUSTED_ORIGINS = ['https://feverpartners.store']