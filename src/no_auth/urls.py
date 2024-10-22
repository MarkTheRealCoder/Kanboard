from . import views

app_name = 'no_auth'

urlpatterns = views.HANDLER.urls()
