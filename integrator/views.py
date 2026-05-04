import json
import os
from django.conf import settings
from django.http import JsonResponse
from .tasks import process_erp_object

def sync_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    file_path = os.path.join(settings.BASE_DIR, "erp_data.json")

    if not os.path.exists(file_path):
        return JsonResponse({"error": "erp_data.json not found"}, status=404)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # očekáváme např. list objektů
    if not isinstance(data, list):
        return JsonResponse({"error": "JSON must be a list of objects"}, status=400)
    
    process_erp_object.delay(data)

    return JsonResponse({
        "status": "ok",
        "sent_tasks": len(data)
    })
