from .models import Notification


def top_notifications(request):
    return {'top_notifications': Notification.objects.all()}
