from .models import Notification


def top_notifications(request):
    if request.user.is_authenticated:
        return {'top_notifications': Notification.objects.filter(user=request.user)}
    else:
        return {'top_notifications': Notification.objects.all()}
