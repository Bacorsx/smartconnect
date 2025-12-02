from django.http import Http404

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from zonas.models import Departamento
from sensores.models import Sensor, Barrera, EventoAcceso
from .serializers import (
    DepartamentoSerializer,
    SensorSerializer,
    BarreraSerializer,
    EventoAccesoSerializer,
    EventoCreateSerializer,
)
from .permissions import IsAdminOrReadOnly


# ---------- Endpoints informativos ----------

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health(request):
    return Response({"status": "ok"})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def info(request):
    return Response({
        "autor": "Isaac Catalán",
        "institucion": "INACAP",
        "asignatura": "Programación Back End",
        "proyecto": "SmartConnect",
        "descripcion": (
            "API RESTful para gestión de sensores RFID, zonas, "
            "eventos de acceso y barrera."
        ),
        "version": "1.0"
    })


# ---------- ViewSets CRUD ----------

class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound("Departamento / zona no encontrada.")


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.select_related('departamento', 'usuario')
    serializer_class = SensorSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound("Sensor no encontrado.")

    # Acción extra para cambiar estado desde la API
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        sensor = self.get_object()
        nuevo_estado = request.data.get('estado')

        serializer = SensorSerializer(
            sensor,
            data={'estado': nuevo_estado},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class BarreraViewSet(viewsets.ModelViewSet):
    queryset = Barrera.objects.all()
    serializer_class = BarreraSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound("Barrera no encontrada.")

    @action(detail=True, methods=['post'])
    def abrir(self, request, pk=None):
        barrera = self.get_object()
        barrera.estado = 'ABIERTA'
        barrera.save()

        EventoAcceso.objects.create(
            sensor=None,
            usuario=request.user,
            tipo='MANUAL',
            accion='ABRIR',
            resultado='PERMITIDO',
            detalle='Apertura manual desde API',
        )
        return Response(self.get_serializer(barrera).data)

    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        barrera = self.get_object()
        barrera.estado = 'CERRADA'
        barrera.save()

        EventoAcceso.objects.create(
            sensor=None,
            usuario=request.user,
            tipo='MANUAL',
            accion='CERRAR',
            resultado='PERMITIDO',
            detalle='Cierre manual desde API',
        )
        return Response(self.get_serializer(barrera).data)


class EventoAccesoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Historial de eventos (solo lectura).
    Admin y Operador pueden ver.
    """
    queryset = EventoAcceso.objects.select_related('sensor', 'usuario')
    serializer_class = EventoAccesoSerializer
    permission_classes = [IsAdminOrReadOnly]


# ---------- Crear evento + controlar barrera ----------

class EventoCreateAPI(APIView):
    """
    Recibe uid + acción, decide PERMITIDO/DENEGADO y actualiza barrera si corresponde.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EventoCreateSerializer(data=request.data)

        if serializer.is_valid():
            evento = serializer.save()

            return Response({
                "mensaje": "Evento procesado correctamente",
                "sensor": evento.sensor.uid,
                "resultado": evento.resultado,
                "accion": evento.accion,
                "tipo": evento.tipo,
                "barrera_estado": (
                    Barrera.objects.first().estado
                    if Barrera.objects.exists() else "SIN_BARRERA"
                ),
                "fecha": evento.fecha_hora
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- Endpoint especial: intento de acceso (para NodeMCU) ----------

@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # o IsAuthenticated si quieres protegerlo
def intento_acceso_uid(request):
    uid = request.data.get('uid')

    if not uid:
        raise ValidationError({"uid": "Este campo es requerido."})

    try:
        sensor = Sensor.objects.get(uid=uid)
    except Sensor.DoesNotExist:
        EventoAcceso.objects.create(
            sensor=None,
            usuario=None,
            tipo='INTENTO',
            accion='INTENTO',
            resultado='DENEGADO',
            detalle='UID no registrado en el sistema',
        )
        return Response(
            {"resultado": "DENEGADO", "detalle": "UID no válido"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Sensor existe: validar estado
    if sensor.estado in ['INACTIVO', 'BLOQUEADO', 'PERDIDO']:
        EventoAcceso.objects.create(
            sensor=sensor,
            usuario=sensor.usuario,
            tipo='INTENTO',
            accion='INTENTO',
            resultado='DENEGADO',
            detalle=f"Sensor en estado {sensor.estado}",
        )
        return Response(
            {"resultado": "DENEGADO", "detalle": "Sensor no autorizado"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Acceso permitido
    EventoAcceso.objects.create(
        sensor=sensor,
        usuario=sensor.usuario,
        tipo='INTENTO',
        accion='INTENTO',
        resultado='PERMITIDO',
        detalle='Acceso concedido',
    )
    return Response(
        {"resultado": "PERMITIDO", "detalle": "Acceso autorizado"},
        status=status.HTTP_200_OK,
    )
