from django.db import models

class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
