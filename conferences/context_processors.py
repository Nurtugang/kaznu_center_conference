from .models import Conference

def latest_conference(request):
    return {
        'current_conf': Conference.objects.order_by('-id').first()
    }

def base_site(request):
    from django.conf import settings
    return {
        'BASE_SITE': getattr(settings, 'BASE_SITE')
    }