from django.db import models
from django.conf import settings
from zonas.models import Departamento

class Sensor(models.Model):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('BLOQUEADO', 'Bloqueado'),
        ('PERDIDO', 'Perdido'),
    ]
    
    uid = models.CharField(max_length=64, unique=True)
    alias = models.CharField(max_length=80, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO')
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.uid} - {self.estado}"


class Barrera(models.Model):
    ESTADOS = [
        ('ABIERTA', 'Abierta'),
        ('CERRADA', 'Cerrada'),
    ]

    estado = models.CharField(max_length=10, choices=ESTADOS, default='CERRADA')
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Barrera {self.estado}"


class EventoAcceso(models.Model):
    TIPOS = [
        ('INTENTO', 'Intento'),
        ('MANUAL', 'Manual'),
    ]

    RESULTADOS = [
        ('PERMITIDO', 'Permitido'),
        ('DENEGADO', 'Denegado'),
    ]

    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    accion = models.CharField(max_length=20)  # EJ: ABRIR / CERRAR
    resultado = models.CharField(max_length=12, choices=RESULTADOS)
    detalle = models.CharField(max_length=255, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sensor.uid} - {self.resultado} - {self.fecha_hora}"