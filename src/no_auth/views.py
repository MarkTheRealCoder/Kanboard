from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token

from Kanboard.settings import BASE_DIR
from static.services import RequestHandler, JsonResponses

# Create your views here.
HANDLER = RequestHandler(BASE_DIR / 'db.sqlite3')


@HANDLER.bind('index', '', request="GET")
def index(request): # Display view
    return render(request, 'index.html')


@HANDLER.bind('login', 'login/', request="GET")
def login(request): # Display view
    return render(request, 'login.html')


@HANDLER.bind('register', 'register/', request="GET")
def register(request): # Display view
    return render(request, 'register.html')

