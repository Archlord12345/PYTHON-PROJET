from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from PIL import Image
from pyzbar.pyzbar import decode


def index(request):
    return render(request, "phone/index.html")


@require_POST
def upload(request):
    image_file = request.FILES.get("image")
    if not image_file:
        return JsonResponse({"ok": False, "error": "Aucune image fournie."}, status=400)

    try:
        image = Image.open(image_file)
    except Exception:
        return JsonResponse({"ok": False, "error": "Image invalide."}, status=400)

    results = decode(image)
    if not results:
        return JsonResponse({"ok": False, "error": "Aucun code détecté."}, status=200)

    payload = results[0].data.decode("utf-8", errors="replace")
    return JsonResponse({"ok": True, "text": payload})
