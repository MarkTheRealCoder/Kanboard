from django.shortcuts import render, redirect
from django.urls import reverse

from static.services import RequestHandler
from static.utils.utils import get_user_from

# Create your views here.
HANDLER = RequestHandler()


@HANDLER.bind('index', '', request="GET")
def index(request): # Display view
    """
    Display the index page.
    If the user is logged in, redirect to the dashboard.

    :param request: HttpRequest object
    :return: HttpResponse object
    """

    uuid = get_user_from(request)

    if uuid:
        return redirect(reverse('core:dashboard'))

    return render(request, 'index.html')


@HANDLER.bind('login', 'login/', request="GET")
def login(request): # Display view
    """
    Display the login page.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    return render(request, 'login.html')


@HANDLER.bind('register', 'register/', request="GET")
def register(request): # Display view
    """
    Display the registration page.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    return render(request, 'register.html')

