from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone

from .models import UsuarioApp, UserPerfil, UserPerfilAsignacion


class BootstrapModelForm(forms.ModelForm):
    """Base visual con Bootstrap"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs['class'] = 'form-control'


class UsuarioForm(BootstrapModelForm):
    """
    Formulario correcto para UsuarioApp:
    - NO usa username, first_name, last_name
    - Permite elegir PERFIL (ADMIN / OPERADOR)
    - Maneja password y confirmación
    """

    perfil = forms.ModelChoiceField(
        queryset=UserPerfil.objects.all(),
        label="Perfil",
        help_text="Rol del usuario en SmartConnect"
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        required=False
    )

    password_confirm = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = UsuarioApp
        fields = [
            "email",
            "name",
            "phone",
            "avatar",
            "is_active",
            "is_staff",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si ya existe usuario: cargar su rol activo
        if self.instance.pk and self.instance.active_asignacion:
            self.fields["perfil"].initial = self.instance.active_asignacion.perfil

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get("password")
        pwd2 = cleaned.get("password_confirm")

        # Validar creación de usuario
        if not self.instance.pk:
            if not pwd:
                raise forms.ValidationError("Debes definir una contraseña para el usuario nuevo.")

        # Validar coincidencia de contraseñas
        if pwd or pwd2:
            if pwd != pwd2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
            if pwd and len(pwd) < 8:
                raise forms.ValidationError("La contraseña debe tener mínimo 8 caracteres.")

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        perfil = self.cleaned_data.get("perfil")

        # Guardar contraseña SOLO si se ingresó
        if password:
            user.set_password(password)

        if commit:
            user.save()

            # Cerrar asignaciones anteriores del usuario
            UserPerfilAsignacion.objects.filter(
                user=user,
                ended_at__isnull=True
            ).exclude(perfil=perfil).update(ended_at=timezone.now())

            # Crear o mantener asignación vigente
            asignacion, created = UserPerfilAsignacion.objects.get_or_create(
                user=user,
                perfil=perfil,
                ended_at=None
            )

            user.active_asignacion = asignacion
            user.save()

        return user


class LoginForm(AuthenticationForm):
    """Login con email + password"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
