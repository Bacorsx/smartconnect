from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
from .views import (DepartamentoViewSet, SensorViewSet, BarreraViewSet, 
                    EventoAccesoViewSet, health, info, intento_acceso_uid)

router = DefaultRouter()
router.register('departamentos', DepartamentoViewSet)
router.register('sensores', SensorViewSet)
router.register('barreras', BarreraViewSet)
router.register('eventos', EventoAccesoViewSet)

def api_not_found(request, *args, **kwargs):
    return JsonResponse({"detail": "Ruta no encontrada."}, status=404)

urlpatterns = [
    path('health/',health, name='health'),
    path('info/',info, name='info'),

    path('', include(router.urls)),

    path('acceso/', intento_acceso_uid, name='intento_acceso_uid'),

    path('<path:resource>', api_not_found),

]
