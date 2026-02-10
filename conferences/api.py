from django.http import JsonResponse
from .models import Conference

def active_conferences_api(request):
    conferences = Conference.objects.filter(is_active=True)
    
    data = []
    for conf in conferences:
        data.append({
            "title": conf.title,
            "short_title": conf.short_title,
            "description": conf.description,
            "poster": request.build_absolute_uri(conf.poster.url) if conf.poster else None,
	    "url": request.build_absolute_uri('/')
        })
    
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})
