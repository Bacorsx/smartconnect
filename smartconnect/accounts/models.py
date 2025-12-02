from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator
from django.utils import timezone
from django.db.models import Q
import secrets
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# ============== Validadores ==============

def validate_file_size_2mb(value):
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('El tamaño máximo para el archivo es 2MB.')

# ============== BaseModel ==============

class BaseModel(models.Model):
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# ============== Manager Usuario ==============

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo Email debe ser establecido')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuario debe tener is_superuser=True.')
        return self.create_user(email, name, password, **extra_fields)

# ============== Perfil (rol) ==============

class UserPerfil(BaseModel):
    # usaremos nombres tipo "ADMIN" y "OPERADOR"
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre


# ============== UsuarioApp (AUTH_USER_MODEL) ==============

class UsuarioApp(AbstractBaseUser, PermissionsMixin):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    email = models.EmailField(unique=True, max_length=30)
    name  = models.CharField(max_length=20, blank=False)

    phone = models.CharField(
        max_length=15,
        unique=False,
        blank=True, null=True,
        validators=[RegexValidator(r'^\+?\d{8,12}$', message='El teléfono debe ser un número válido.')],
        help_text="Teléfono de contacto (ej: +56912345678)"
    )

    avatar = models.ImageField(
        upload_to="users/",
        null=True, blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg","jpeg","png","webp"]),
            validate_file_size_2mb
        ],
        help_text="Imagen JPG/PNG. Máx 2MB."
    )

    is_staff  = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    # seguridad extra
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    active_asignacion = models.ForeignKey(
        "UserPerfilAsignacion",
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="usuarios_vigentes"
    )

    objects = CustomUserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['name']

    # ----- Métodos de seguridad -----
    def is_locked(self):
        return self.locked_until and timezone.now() < self.locked_until

    def lock_for_minutes(self, minutes=15):
        self.locked_until = timezone.now() + timezone.timedelta(minutes=minutes)
        self.failed_login_attempts = 0
        self.save(update_fields=["locked_until", "failed_login_attempts"])

    # ----- Propiedad de rol compatible con lo que estábamos usando -----
    @property
    def rol(self):
        """
        Devuelve el nombre del perfil vigente (ej: 'ADMIN', 'OPERADOR')
        para que el resto del sistema (mixins, templates) pueda usar user.rol.
        """
        if self.active_asignacion and self.active_asignacion.perfil:
            return self.active_asignacion.perfil.nombre
        return None

    # constantes de ayuda para comparar
    ROL_ADMIN = 'ADMIN'
    ROL_OPERADOR = 'OPERADOR'

    def __str__(self):
        return self.email


# ============== Código de recuperación de contraseña ==============

class PasswordResetCode(models.Model):
    user = models.ForeignKey(UsuarioApp, on_delete=models.CASCADE, related_name="reset_codes")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["created_at"]),
        ]

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    def consume(self):
        self.is_active = False
        self.used_at = timezone.now()
        self.save(update_fields=["is_active", "used_at"])

    @staticmethod
    def generate_6_digits():
        import secrets
        return f"{secrets.randbelow(1_000_000):06d}"


# ============== Asignación de perfil (histórico + vigente) ==============

class UserPerfilAsignacion(BaseModel):
    user   = models.ForeignKey(UsuarioApp, on_delete=models.CASCADE, related_name="asignaciones")
    perfil = models.ForeignKey(UserPerfil, on_delete=models.CASCADE, related_name="asignaciones")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "ended_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(ended_at__isnull=True),
                name="uniq_user_asignacion_vigente"
            )
        ]

    @property
    def vigente(self):
        return self.ended_at is None

    def finalizar(self, when=None):
        if self.ended_at is None:
            self.ended_at = when or timezone.now()
            self.save(update_fields=["ended_at"])

    def __str__(self):
        return f"{self.user.email} → {self.perfil.nombre}"
