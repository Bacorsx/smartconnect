# api/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    NotAuthenticated,
    PermissionDenied,
    NotFound
)
from django.http import Http404

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        detail = response.data.get("detail", None)

        if isinstance(exc, ValidationError):
            # 400 -> errores de validación
            response.data = {
                "detail": "Error de validación.",
                "errors": response.data,  # aquí vienen los campos
            }
        elif isinstance(exc, NotAuthenticated):
            # 401
            response.data = {
                "detail": "Autenticación requerida."
            }
        elif isinstance(exc, PermissionDenied):
            # 403
            response.data = {
                "detail": "No tienes permisos para realizar esta acción."
            }
        elif isinstance(exc, (NotFound, Http404)):
            # 404 objeto no encontrado
            response.data = {
                "detail": "Recurso no encontrado."
            }
        return response
    return response
