from . import views
from .models import APP_NAME

app_name = APP_NAME

urlpatterns = views.HANDLER.urls()