from .models import Conference

def latest_conference(request):
    return {
        'current_conf': Conference.objects.order_by('-id').first()
    }