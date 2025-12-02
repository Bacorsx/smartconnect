from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from accounts.mixins import RolRequeridoMixin
from accounts.models import UsuarioApp
from .models import Departamento
from .forms import DepartamentoForm

class DepartamentoListView(RolRequeridoMixin, ListView):
    model = Departamento
    template_name = 'zonas/departamento_list.html'
    context_object_name = 'departamentos'
    roles_permitidos = [UsuarioApp.ROL_ADMIN, UsuarioApp.ROL_OPERADOR]  # ambos pueden ver

class DepartamentoCreateView(RolRequeridoMixin, CreateView):
    model = Departamento
    form_class = DepartamentoForm
    template_name = 'includes/base_form.html'
    success_url = reverse_lazy('departamento_list')
    roles_permitidos = [UsuarioApp.ROL_ADMIN]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Crear departamento / zona'
        ctx['submit_label'] = 'Guardar'
        ctx['cancel_url'] = self.success_url
        return ctx

class DepartamentoUpdateView(DepartamentoCreateView, UpdateView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Editar departamento / zona'
        return ctx

class DepartamentoDeleteView(RolRequeridoMixin, DeleteView):
    model = Departamento
    template_name = 'includes/base_confirm_delete.html'
    success_url = reverse_lazy('departamento_list')
    roles_permitidos = [UsuarioApp.ROL_ADMIN]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Eliminar departamento / zona'
        ctx['cancel_url'] = self.success_url
        return ctx
