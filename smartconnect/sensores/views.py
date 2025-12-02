from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from accounts.mixins import RolRequeridoMixin
from accounts.models import UsuarioApp
from .models import Sensor, Barrera
from .forms import SensorForm, BarreraForm

class SensorListView(RolRequeridoMixin, ListView):
    model = Sensor
    template_name = 'sensores/sensor_list.html'
    roles_permitidos = [UsuarioApp.ROL_ADMIN, UsuarioApp.ROL_OPERADOR]


class SensorCreateView(RolRequeridoMixin, CreateView):
    model = Sensor
    form_class = SensorForm
    template_name = 'includes/base_form.html'
    success_url = reverse_lazy('sensor_list')
    roles_permitidos = [UsuarioApp.ROL_ADMIN]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Registrar Sensor'
        ctx['submit_label'] = 'Guardar'
        ctx['cancel_url'] = self.success_url
        return ctx


class SensorUpdateView(SensorCreateView, UpdateView):
    roles_permitidos = [UsuarioApp.ROL_ADMIN]
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Editar Sensor'
        return ctx


class SensorDeleteView(RolRequeridoMixin, DeleteView):
    model = Sensor
    template_name = 'includes/base_confirm_delete.html'
    success_url = reverse_lazy('sensor_list')
    roles_permitidos = [UsuarioApp.ROL_ADMIN]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Eliminar Sensor'
        ctx['cancel_url'] = self.success_url
        return ctx
