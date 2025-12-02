from rest_framework import serializers
from zonas.models import Departamento
from sensores.models import Sensor, Barrera, EventoAcceso


# ---------- Departamento / Zona ----------

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = ['id', 'nombre', 'descripcion', 'is_active']

    # Validación por campo
    def validate_nombre(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "El nombre debe tener mínimo 3 caracteres."
            )
        return value

    # Validación global
    def validate(self, data):
        if not data.get('is_active', True) and not data.get('descripcion'):
            raise serializers.ValidationError(
                "Si desactivas un departamento, debes agregar una descripción/motivo."
            )
        return data


# ---------- Sensor RFID ----------

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = [
            'id', 'uid', 'alias', 'estado',
            'departamento', 'usuario',
            'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']

    def validate_uid(self, value):
        if len(value.strip()) < 4:
            raise serializers.ValidationError(
                "El UID debe tener al menos 4 caracteres."
            )
        return value

    def validate_estado(self, value):
        estados_validos = [choice[0] for choice in Sensor.ESTADOS]
        if value not in estados_validos:
            raise serializers.ValidationError("Estado de sensor no válido.")
        return value

    def validate(self, data):
        # ejemplo: si sensor está BLOQUEADO no puede tener usuario nulo
        if data.get('estado') == 'BLOQUEADO' and data.get('usuario') is None:
            raise serializers.ValidationError(
                "Un sensor BLOQUEADO debe estar asociado a un usuario responsable."
            )
        return data


# ---------- Barrera ----------

class BarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barrera
        fields = ['id', 'estado', 'actualizado_en']
        read_only_fields = ['id', 'actualizado_en']


# ---------- Evento de acceso (lectura) ----------

class EventoAccesoSerializer(serializers.ModelSerializer):
    sensor_uid = serializers.CharField(source='sensor.uid', read_only=True)
    usuario_email = serializers.EmailField(source='usuario.email', read_only=True)

    class Meta:
        model = EventoAcceso
        fields = [
            'id',
            'sensor', 'sensor_uid',
            'usuario', 'usuario_email',
            'tipo', 'accion', 'resultado',
            'detalle', 'fecha_hora',
        ]


# ---------- Evento de acceso (creación + barrera) ----------

class EventoCreateSerializer(serializers.Serializer):
    """
    Recibe un UID y una acción (ABRIR/CERRAR), decide si se permite
    y opcionalmente actualiza la barrera.
    """
    uid = serializers.CharField()
    accion = serializers.ChoiceField(choices=["ABRIR", "CERRAR"])
    tipo = serializers.ChoiceField(choices=["INTENTO", "MANUAL"], default="INTENTO")
    detalle = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        uid = data["uid"]

        try:
            sensor = Sensor.objects.get(uid=uid)
        except Sensor.DoesNotExist:
            raise serializers.ValidationError({"uid": "Sensor no encontrado"})

        data["sensor"] = sensor
        return data

    def create(self, validated_data):
        sensor = validated_data["sensor"]
        accion = validated_data["accion"]
        tipo = validated_data["tipo"]
        detalle = validated_data.get("detalle", "")

        # Determinar si el acceso es permitido
        if sensor.estado in ["BLOQUEADO", "PERDIDO", "INACTIVO"]:
            resultado = "DENEGADO"
        else:
            resultado = "PERMITIDO"
            # Control de barrera solo si es permitido
            barrera = Barrera.objects.first()
            if barrera:
                barrera.estado = "ABIERTA" if accion == "ABRIR" else "CERRADA"
                barrera.save()

        evento = EventoAcceso.objects.create(
            sensor=sensor,
            usuario=sensor.usuario,  # Usuario vinculado al sensor (si existe)
            tipo=tipo,
            accion=accion,
            resultado=resultado,
            detalle=detalle
        )

        return evento
