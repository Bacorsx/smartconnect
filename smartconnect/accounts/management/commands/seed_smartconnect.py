from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import UsuarioApp, UserPerfil, UserPerfilAsignacion
from zonas.models import Departamento
from sensores.models import Sensor, Barrera, EventoAcceso


class Command(BaseCommand):
    help = "Carga datos iniciales para SmartConnect (perfiles, usuarios, zonas, sensores)"

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.WARNING("Iniciando carga de datos..."))

        # ==================================
        # 1. Perfiles
        # ==================================
        perfiles = ["ADMIN", "OPERADOR"]
        perfil_objs = {}

        for nombre in perfiles:
            obj, created = UserPerfil.objects.get_or_create(nombre=nombre)
            perfil_objs[nombre] = obj
            msg = "CREADO" if created else "EXISTE"
            self.stdout.write(f"Perfil {nombre}: {msg}")

        # ==================================
        # 2. Usuarios base
        # ==================================

        # ADMIN
        admin_email = "admin@smartconnect.cl"
        admin, created = UsuarioApp.objects.get_or_create(
            email=admin_email,
            defaults={
                "name": "Admin General",
                "is_active": True,
                "is_staff": True,
            }
        )
        if created:
            admin.set_password("Admin12345")
            admin.save()
            self.stdout.write(self.style.SUCCESS(f"Usuario ADMIN creado: {admin_email} / Admin12345"))
        else:
            self.stdout.write(f"Usuario ADMIN ya existe: {admin_email}")

        # asignación perfil admin
        UserPerfilAsignacion.objects.update_or_create(
            user=admin,
            perfil=perfil_objs["ADMIN"],
            ended_at=None,
            defaults={}
        )
        admin.active_asignacion = UserPerfilAsignacion.objects.get(user=admin, ended_at=None)
        admin.save()

        # OPERADOR
        op_email = "operador@smartconnect.cl"
        operador, created = UsuarioApp.objects.get_or_create(
            email=op_email,
            defaults={
                "name": "Operador Base",
                "is_active": True,
                "is_staff": False,
            }
        )
        if created:
            operador.set_password("Operador123")
            operador.save()
            self.stdout.write(self.style.SUCCESS(f"Usuario OPERADOR creado: {op_email} / Operador123"))
        else:
            self.stdout.write(f"Usuario OPERADOR ya existe: {op_email}")

        # asignación perfil operador
        UserPerfilAsignacion.objects.update_or_create(
            user=operador,
            perfil=perfil_objs["OPERADOR"],
            ended_at=None,
            defaults={}
        )
        operador.active_asignacion = UserPerfilAsignacion.objects.get(user=operador, ended_at=None)
        operador.save()

        # ==================================
        # 3. Departamentos (zonas)
        # ==================================
        zonas = ["Entrada Principal", "Bodega", "Administración"]
        zona_objs = []

        for z in zonas:
            obj, created = Departamento.objects.get_or_create(nombre=z)
            zona_objs.append(obj)
            msg = "CREADO" if created else "EXISTE"
            self.stdout.write(f"Zona {z}: {msg}")

        # ==================================
        # 4. Sensores
        # ==================================
        sensores_seed = [
            ("A1B2C3D4", "Llavero Admin"),
            ("11223344", "Tarjeta Operador"),
            ("99887766", "Sensor Portón"),
        ]

        for uid, alias in sensores_seed:
            sensor, created = Sensor.objects.get_or_create(
                uid=uid,
                defaults={
                    "alias": alias,
                    "estado": "ACTIVO",
                    "departamento": zona_objs[0],  # Entrada principal
                    "usuario": admin if alias == "Llavero Admin" else None,
                }
            )
            msg = "CREADO" if created else "EXISTE"
            self.stdout.write(f"Sensor {uid}: {msg}")

        # ==================================
        # 5. Barrera
        # ==================================
        barrera, created = Barrera.objects.get_or_create(
            id=1,
            defaults={"estado": "CERRADA"}
        )
        self.stdout.write(f"Barrera inicial: {'CREADA' if created else 'EXISTE'}")

        # ==================================
        # 6. Evento ejemplo
        # ==================================
        primer_sensor = Sensor.objects.first()
        if primer_sensor:
            EventoAcceso.objects.create(
                sensor=primer_sensor,
                usuario=admin,
                tipo="INTENTO",
                accion="ABRIR",
                resultado="PERMITIDO",
                detalle="Acceso registrado automáticamente por seed.",
            )
            self.stdout.write("Evento de acceso de prueba creado.")

        self.stdout.write(self.style.SUCCESS("\n✔ SEED COMPLETADO CORRECTAMENTE ✔"))
