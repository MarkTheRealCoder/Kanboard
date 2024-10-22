from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import requires_csrf_token

from Kanboard.settings import BASE_DIR
from static.services import RequestHandler, JsonResponses
from static.utils.utils import get_user_from

# Create your views here.
HANDLER = RequestHandler(BASE_DIR / 'db.sqlite3')


@HANDLER.bind('index', '', request="GET")
def index(request): # Display view

    uuid = get_user_from(request)

    if uuid:
        return redirect(reverse('core:dashboard'))

    return render(request, 'index.html')


@HANDLER.bind('login', 'login/', request="GET")
def login(request): # Display view
    return render(request, 'login.html')


@HANDLER.bind('register', 'register/', request="GET")
def register(request): # Display view
    return render(request, 'register.html')

