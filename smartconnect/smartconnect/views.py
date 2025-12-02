from django.http import JsonResponse
from django.shortcuts import render

def custom_404_view(request, exception):
    if request.path.startswith("/api/"):
        return JsonResponse(
            {"detail": "Ruta no encontrada."},
            status=404,
        )

    return render(request, "errors/404.html", status=404)