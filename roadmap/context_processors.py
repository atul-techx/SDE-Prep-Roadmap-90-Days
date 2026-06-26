from .models import Notice

def notices_processor(request):
    if request.user.is_authenticated:
        notices = Notice.objects.filter(is_active=True).order_by('-created_at')[:5]
        return {'all_active_notices': notices, 'has_notices': notices.exists()}
    return {}
