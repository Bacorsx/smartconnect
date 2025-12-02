from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView

from .models import UsuarioApp
from .forms import UsuarioForm, LoginForm
from .mixins import RolRequeridoMixin


# ========== AUTH ==========

class UserLoginView(LoginView):
    """
    Login usando UsuarioApp como AUTH_USER_MODEL.
    Usa LoginForm (subclase de AuthenticationForm).
    """
    form_class = LoginForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        messages.success(self.request, "Has iniciado sesión correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Credenciales inválidas.")
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    """
    Cierre de sesión simple.
    """
    next_page = reverse_lazy("login")


# ========== CRUD USUARIOS ==========

class UsuarioListView(RolRequeridoMixin, ListView):
    model = UsuarioApp
    template_name = "accounts/usuario_list.html"
    context_object_name = "usuarios"
    roles_permitidos = [UsuarioApp.ROL_ADMIN]


class UsuarioCreateView(RolRequeridoMixin, CreateView):
    model = UsuarioApp
    form_class = UsuarioForm
    template_name = "includes/base_form.html"
    success_url = reverse_lazy("usuario_list")
    roles_permitidos = [UsuarioApp.ROL_ADMIN]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Crear usuario"
        ctx["submit_label"] = "Guardar"
        ctx["cancel_url"] = self.success_url
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Usuario creado correctamente.")
        return super().form_valid(form)


class UsuarioUpdateView(UsuarioCreateView, UpdateView):
    roles_permitidos = [UsuarioApp.ROL_ADMIN]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Editar usuario"
        return ctx


class UsuarioDeleteView(RolRequeridoMixin, DeleteView):
    model = UsuarioApp
    template_name = "includes/base_confirm_delete.html"
    success_url = reverse_lazy("usuario_list")
    roles_permitidos = [UsuarioApp.ROL_ADMIN]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Eliminar usuario"
        ctx["cancel_url"] = self.success_url
        return ctx

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Usuario eliminado correctamente.")
        return super().delete(request, *args, **kwargs)
