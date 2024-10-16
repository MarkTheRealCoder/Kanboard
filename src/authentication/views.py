from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Kanboard.settings import BASE_DIR

from static.services import RequestHandler, DBRequestBuilder, ModelsAttributeError, UserValidations, JsonResponses
from .models import User
import re

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


@HANDLER.bind("registration_submission", "register/submit/")
def registration_submission(request): # Working view
    if request.method != 'POST':
        return JsonResponses.response(JsonResponses.ERROR, "Invalid request")

    required_fields = {
        'username': request.POST.get('username', None),
        'email': request.POST.get('email', None),
        'password': request.POST.get('password', None),
        'name': request.POST.get('name', None),
        'surname': request.POST.get('surname', None)
    }

    uuid = ""
    try:
        uuid = UserValidations(User, **required_fields).result().generate_uuid()
    except ModelsAttributeError as e:
        return JsonResponses.response(JsonResponses.ERROR, f'Something went wrong:\n{str(e)}.')

    # user = User.objects.create_user(uuid=uuid, **required_fields)

    request.session['uuid'] = uuid
    request.session.set_expiry(0)
    return redirect(reverse('core:dashboard'))


@HANDLER.bind("login_submission", "login/submit/")
def login_submission(request): # Working view
    print(request.POST)
    key = request.POST.get('key', None)
    password = request.POST.get('password', None)
    field = 'email'

    try:
        UserValidations(User, **{field: key}).result()
    except ModelsAttributeError as e:
        if not e.is_existence():
            field = 'username'

    request = {field: key, "password":password}
    user = User.objects.filter(**request).first()

    if not user:
        return JsonResponses.response(JsonResponses.ERROR, "Username o password non corretti")

    request.session['uuid'] = user.uuid
    request.session.set_expiry(0)
    return redirect(reverse('core:dashboard'))


@HANDLER.bind('logout', 'logout/')
def logout(request): # Working view
    request.session.flush()
    return redirect(reverse('no_auth:index'))


data = (
    DBRequestBuilder("user_details", "No user found with this ID!")
    .select("username", "email", "image", "name", "surname", "date_joined")
    .from_table("user")
    .where("uuid = PARAM(uuid)"),
)

@HANDLER.bind("user_details", "account/", *data)
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
