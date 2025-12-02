from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .models import UsuarioApp

class RolRequeridoMixin(LoginRequiredMixin):
    roles_permitidos = None  # lista de strings, ej: ['ADMIN']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if self.roles_permitidos is not None:
            rol_usuario = getattr(request.user, 'rol', None)
            if rol_usuario not in self.roles_permitidos:
                raise PermissionDenied("No tienes permiso para acceder a esta vista.")
        return super().dispatch(request, *args, **kwargs)
