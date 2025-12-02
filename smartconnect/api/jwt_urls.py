# api/jwt_urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


class LoginView(TokenObtainPairView):
    # Forzamos que este endpoint siempre permita acceso sin autenticación previa
    permission_classes = [AllowAny]


urlpatterns = [
    # IMPORTANTÍSIMO: marcar la vista como csrf_exempt
    path('login/', csrf_exempt(LoginView.as_view()), name='jwt_login'),
    path('refresh/', csrf_exempt(TokenRefreshView.as_view()), name='jwt_refresh'),
]