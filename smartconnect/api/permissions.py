from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin: CRUD completo
    Operador: solo lectura
    """

    def has_permission(self, request, view):
        # métodos seguros → GET / HEAD / OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # métodos de escritura → POST, PUT, PATCH, DELETE
        return (
            request.user.is_authenticated and 
            getattr(request.user, "rol", None) == "ADMIN"
        )
