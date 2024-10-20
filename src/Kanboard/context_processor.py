# context_processors.py
from django.conf import settings

from Kanboard.settings import MEDIA_URL


def media_url(request):
    return {'MEDIA_URL': MEDIA_URL}
