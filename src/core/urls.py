from django.urls import path

from authentication import views

app_name = 'core'

urlpatterns = views.HANDLER.urls()