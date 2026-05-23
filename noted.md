# Secure API Authentication System with Django REST Framework

## Stack
- Django
- Django REST Framework (DRF)
- JWT Authentication
- Refresh Tokens
- Role-based permissions
- Rate limiting
- CORS protection
- Environment variables
- Password validation
- Secure headers

---

# 1. Install Dependencies

```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers python-dotenv
```

---

# 2. Create Project

```bash
django-admin startproject config
cd config
python manage.py startapp accounts
```

---

# 3. settings.py

Add apps:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',

    'accounts',
]
```

---

Add middleware:

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

---

# 4. REST Framework + JWT

```python
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],

    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/minute',
        'user': '100/minute',
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,

    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

---

# 5. Security Configuration

```python
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

# 6. CORS Settings

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]

CORS_ALLOW_CREDENTIALS = True
```

---

# 7. Environment Variables (.env)

Create `.env`

```env
SECRET_KEY=your-secret-key
DEBUG=False
```

---

Load dotenv:

```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'
```

---

# 8. accounts/serializers.py

```python
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
```

---

# 9. accounts/views.py

```python
from rest_framework import generics, permissions
from .serializers import RegisterSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


from rest_framework.views import APIView


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
        })
```

---

# 10. accounts/urls.py

```python
from django.urls import path
from .views import RegisterView, ProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/', ProfileView.as_view(), name='profile'),
]
```

---

# 11. config/urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
]
```

---

# 12. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# 13. Create Admin User

```bash
python manage.py createsuperuser
```

---

# 14. Start Server

```bash
python manage.py runserver
```

---

# 15. API Endpoints

## Register

```http
POST /api/auth/register/
```

Body:

```json
{
  "username": "admin",
  "email": "admin@gmail.com",
  "password": "StrongPass123!",
  "password2": "StrongPass123!"
}
```

---

## Login

```http
POST /api/auth/login/
```

Body:

```json
{
  "username": "admin",
  "password": "StrongPass123!"
}
```

Response:

```json
{
  "access": "jwt-access-token",
  "refresh": "jwt-refresh-token"
}
```

---

## Get Profile

```http
GET /api/auth/profile/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

# 16. Advanced Security Recommendations

## Password Policy

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

---

## Use HTTPS in Production

Deploy behind:
- Nginx
- Cloudflare
- HTTPS SSL certificate

---

## Store Tokens Securely

Frontend recommendations:
- Store access token in memory
- Store refresh token in HTTP-only cookies
- Never store JWT in localStorage for sensitive apps

---

## Add Email Verification

Recommended packages:

```bash
pip install django-allauth
```

---

## Add Login Attempt Protection

```bash
pip install django-axes
```

---

## Add API Logging

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
}
```

---

# 17. Recommended Production Stack

Backend:
- Django
- Gunicorn
- PostgreSQL
- Redis

Server:
- Ubuntu VPS
- Nginx
- Cloudflare

Deployment:
- Docker
- GitHub Actions CI/CD

---

# 18. Recommended Folder Structure

```text
project/
│
├── accounts/
│   ├── migrations/
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── models.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── .env
├── manage.py
└── requirements.txt
```

---

# 19. Example Protected Request

```bash
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

# 20. Security Checklist

- JWT authentication
- Refresh token rotation
- Password validation
- HTTPS only
- Rate limiting
- CORS restriction
- Secure cookies
- XSS protection
- CSRF protection
- HSTS enabled
- Environment variables
- Login throttling
- Token expiration

---

# 21. Optional Features

You can extend this system with:

- Google Login
- GitHub OAuth
- Email OTP
- Two-Factor Authentication (2FA)
- Role-based Access Control (RBAC)
- API Key authentication
- Audit logging
- Device/session management
- Refresh token blacklist
- Admin dashboard

