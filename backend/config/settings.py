"""
Django settings for config project.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY não definida. Defina a variável de ambiente SECRET_KEY "
        "(ex.: no arquivo backend/.env)."
    )

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# A chave do docker-compose.yml é pública (está no repositório) e só vale no
# ambiente local. Com DEBUG desligado, o site recusa subir com ela.
if not DEBUG and SECRET_KEY.startswith('chave-apenas-para-desenvolvimento'):
    raise RuntimeError(
        "SECRET_KEY de desenvolvimento em uso com DEBUG=False. "
        "Defina uma SECRET_KEY própria no ambiente de produção."
    )

ALLOWED_HOSTS = [h for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h]

# Só entra em vigor quando DEBUG=False (publicação de verdade); em
# desenvolvimento local (DEBUG=True) fica tudo como já era, sem exigir
# HTTPS nem cookies marcados como seguros.
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# Só é seguro confiar no cabeçalho X-Forwarded-Proto quando existe de fato um
# proxy reverso na frente do Django removendo qualquer valor que o cliente
# tente forjar; por isso é opt-in por variável de ambiente, não ligado
# automaticamente junto com SECURE_SSL_REDIRECT. Sem isso configurado atrás de
# um proxy que termina TLS, o Django nunca vê a requisição como segura e
# entra em loop de redirecionamento.
if os.environ.get('BEHIND_PROXY', 'False') == 'True':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Domínios (com https://) autorizados a enviar formulários ao Django, como o
# login do /admin. Necessário em produção quando o admin é servido por HTTPS.
CSRF_TRUSTED_ORIGINS = [h for h in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if h]


# Application definition

INSTALLED_APPS = [
    # Tema do /admin. Precisa vir antes de django.contrib.admin para que seus
    # templates substituam os do Django.
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Depois de staticfiles de propósito: o collectstatic do cloudinary_storage
    # lê STATICFILES_STORAGE (removido no Django 5.1) e quebraria o deploy.
    'cloudinary_storage',
    'cloudinary',
    'website.apps.WebsiteConfig',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Serve os arquivos estáticos (CSS/JS do /admin) em produção, sem nginx.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Precisa vir antes do CommonMiddleware para responder às requisições
    # de CORS antes que ele as redirecione.
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'website.middleware.PublicApiCacheMiddleware',
]

# Segundos que o navegador pode reaproveitar as respostas de leitura da API.
# Uma edição no admin leva até esse tempo para aparecer. Use 0 para desligar.
API_CACHE_SECONDS = int(os.environ.get('API_CACHE_SECONDS', '60'))

# Endereço secreto que o Render dá para reconstruir o frontend (Settings > Deploy
# Hook). Opcional: sem ele, mudar a marca ou a descrição do site exige disparar
# o deploy do frontend à mão.
RENDER_FRONTEND_DEPLOY_HOOK = os.environ.get('RENDER_FRONTEND_DEPLOY_HOOK', '')

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# Em produção, os provedores de Postgres (Neon, Supabase, Render...) entregam
# uma única URL de conexão; basta colocá-la em DATABASE_URL. Sem ela, usa as
# variáveis DB_* do docker-compose local.
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(os.environ['DATABASE_URL'], conn_max_age=600),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'iccsite'),
            'USER': os.environ.get('DB_USER', 'iccuser'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'iccpassword'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

# Correções de grafia da tradução em português do Django (ver locale/). A pasta do
# projeto vem antes da do Django, então as entradas dela valem.
LOCALE_PATHS = [BASE_DIR / 'locale']

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

# Tema do /admin (django-unfold). A escala "primary" é o vermelho da marca
# (o #b20000 do site fica perto do tom 700), no formato oklch que o Unfold usa.
UNFOLD = {
    'SITE_TITLE': 'Admin ICC',
    'SITE_HEADER': 'Insper Consulting Club',
    'SITE_SUBHEADER': 'Conteúdo do site',
    'SITE_URL': None,
    'COLORS': {
        'primary': {
            '50': 'oklch(97.1% .013 17.38)',
            '100': 'oklch(93.6% .032 17.717)',
            '200': 'oklch(88.5% .062 18.334)',
            '300': 'oklch(80.8% .114 19.571)',
            '400': 'oklch(70.4% .191 22.216)',
            '500': 'oklch(63.7% .237 25.331)',
            '600': 'oklch(57.7% .245 27.325)',
            '700': 'oklch(50.5% .213 27.518)',
            '800': 'oklch(44.4% .177 26.899)',
            '900': 'oklch(39.6% .141 25.723)',
            '950': 'oklch(25.8% .092 26.042)',
        },
    },
}

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'website' / 'static'

# Media files (Upload) — armazenados no Cloudinary em produção/dev compartilhado
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'images'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}
# Sem credenciais Cloudinary (ambiente local sem acesso ao dev compartilhado),
# cai para armazenamento em disco (MEDIA_ROOT) em vez de quebrar os uploads.
# Desde o Django 5.1 isso é configurado em STORAGES; DEFAULT_FILE_STORAGE é
# ignorado e os uploads iriam para o disco do servidor, perdidos a cada deploy.
STORAGES = {
    'default': {
        'BACKEND': (
            'cloudinary_storage.storage.MediaCloudinaryStorage'
            if CLOUDINARY_STORAGE['CLOUD_NAME']
            else 'django.core.files.storage.FileSystemStorage'
        ),
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurável por ambiente pelo mesmo motivo de ALLOWED_HOSTS: o domínio
# real de produção só existe quando a hospedagem for definida. Sem
# CORS_ALLOWED_ORIGINS no ambiente, cai nas portas padrão de desenvolvimento.
CORS_ALLOWED_ORIGINS = [h for h in os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://localhost:3000'
).split(',') if h]
