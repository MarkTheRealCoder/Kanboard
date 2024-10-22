from django.shortcuts import render, redirect
from django.urls import reverse

from static.services import RequestHandler
from static.utils.utils import get_user_from

# Create your views here.
HANDLER = RequestHandler()


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

