from typing import re

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Kanboard.settings import BASE_DIR
<<<<<<< HEAD:src/authentication/views.py
from static.services import RequestHandler, ModelsAttributeError, UserValidations, JsonResponses
=======
from static.services import RequestHandler, DBRequestBuilder, ModelsAttributeError, UserValidations, JsonResponses  # , JsonResponses
>>>>>>> master:src/auth/views.py
from .models import User

# Create your views here.

HANDLER = RequestHandler(BASE_DIR / 'db.sqlite3')


@HANDLER.bind('user_management', 'account/changes/')
def user_management(request): # Working view
    id = request.session.get('user_id')
    updates = {
        'name': None,
        'surname': None,
        'password': None,
        'email': None,
    }
    for key in updates.keys():
        if not key in request.POST.keys():
            updates.pop(key)
            continue
        updates[key] = request.POST.get(key)
    if img := request.FILES.get('image', None):
        updates['image'] = request.FILES.get('image')

    user = User.objects.filter(uuid=id).first()

    try:
        UserValidations(User, **updates).result()
    except ModelsAttributeError as e:
        return JsonResponses.response(JsonResponses.ERROR, f'Something went wrong:\n{str(e)}.')
    return JsonResponses.response(JsonResponses.SUCCESS, 'Your account details has been updated successfully.')


@HANDLER.bind('logout', 'logout/')
def logout(request):
    request.session.flush()
<<<<<<< HEAD:src/authentication/views.py
    request.session.set_expiry(0)
    return redirect('index')
=======
    return redirect('index')

data = (
    DBRequestBuilder("auth", "user_details", "No user found with this ID!")
    .select("username", "email", "image", "name", "surname", "date_joined")
    .from_table("user")
    .where("uuid = PARAM(uuid)"),
)


@HANDLER.bind("user_details", "/account", *data)
def user_details_view(request, user_details):
    """
    Executes the query to retrieve user details after login.
    :param request: HttpRequest - The HTTP request object.
    :param user_details: str - The result of the user details query.
    :return: HttpResponse - The rendered HTML page with user details.
    """
    return render(request, "user_details.html", {
        "user": user_details
    })
>>>>>>> master:src/auth/views.py
