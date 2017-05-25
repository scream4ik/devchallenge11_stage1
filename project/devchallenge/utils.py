from django.conf import settings


def show_toolbar(request):
    if not settings.DEBUG:
        return False
    return True
