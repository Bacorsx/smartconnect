from django.urls import path
from .views import (
    SensorListView, SensorCreateView,
    SensorUpdateView, SensorDeleteView
)

urlpatterns = [
    path('', SensorListView.as_view(), name='sensor_list'),
    path('crear/', SensorCreateView.as_view(), name='sensor_create'),
    path('<int:pk>/editar/', SensorUpdateView.as_view(), name='sensor_update'),
    path('<int:pk>/eliminar/', SensorDeleteView.as_view(), name='sensor_delete'),
]
