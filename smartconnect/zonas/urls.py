from django.urls import path
from .views import (
    DepartamentoListView, DepartamentoCreateView,
    DepartamentoUpdateView, DepartamentoDeleteView
)

urlpatterns = [
    path('', DepartamentoListView.as_view(), name='departamento_list'),
    path('crear/', DepartamentoCreateView.as_view(), name='departamento_create'),
    path('<int:pk>/editar/', DepartamentoUpdateView.as_view(), name='departamento_update'),
    path('<int:pk>/eliminar/', DepartamentoDeleteView.as_view(), name='departamento_delete'),
]
