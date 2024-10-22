from django.urls import path

from .models import APP_NAME
from . import views

app_name = APP_NAME

urlpatterns = views.HANDLER.urls()