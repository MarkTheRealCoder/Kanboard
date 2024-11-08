from datetime import timezone, datetime

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import requires_csrf_token

from static.services import RequestHandler, ModelsAttributeError, UserValidations
from static.utils.utils import response_error, get_user_from, response_success, get_user, no_timezone
from .models import User

# Create your views here.
HANDLER = RequestHandler()


@HANDLER.bind("registration_submission", "register/submit/", request="POST", session=False)
@requires_csrf_token
def registration_submission(request):
    """
    Registers a new user to the database.
    Requires the request to be POST.

    :param request: HttpRequest - The HTTP request object.
    :return: HttpResponse - The rendered 'dashboard' HTML page.
    """

    required_fields = {
        'name': request.POST.get('name', None),
        'surname': request.POST.get('surname', None),
        'username': request.POST.get('username', None),
        'email': request.POST.get('email', None),
        'password': request.POST.get('password', None),
        'date_joined': no_timezone(datetime.now()),
        'last_login': no_timezone(datetime.now())
    }

    try:
        uuid = str(UserValidations(User, **required_fields).result().generate_uuid())
    except ModelsAttributeError:
        return response_error("Could not register your account.")

    User.objects.create(uuid=uuid, **required_fields).save()

    request.session['uuid'] = uuid
    request.session.set_expiry(0)

    return redirect(reverse('core:dashboard'))


@HANDLER.bind("login_submission", "login/submit/", request="POST", session=False)
@requires_csrf_token
def login_submission(request):
    """
    Logs in an existing user to the dashboard.
    Requires the request to be POST.

    :param request: HttpRequest - The HTTP request object.
    :return: HttpResponse - The rendered 'dashboard' HTML page.
    """

    field = 'email'
    key = request.POST.get('key', None)
    password = request.POST.get('password', None)

    while True:
        try:
            UserValidations(User, **{field: key}).result()
            break
        except ModelsAttributeError as e:
            if not e.is_existence():
                if field == 'username':
                    return response_error("Username or Email are incorrect.")
                field = 'username'
            else:
                break

    to_filter = { field: key, "password": password }
    user = User.objects.filter(**to_filter).first()

    if not user:
        return response_error(f"{field.title()} or password are incorrect.")

    user.last_login = no_timezone(datetime.now())

    request.session['uuid'] = user.uuid.hex
    request.session.set_expiry(0)

    return redirect(reverse('core:dashboard'))


@HANDLER.bind('user_management', 'account/changes/', request="POST", session=True)
@requires_csrf_token
def user_management(request):
    """
    Updates the user details in the database.
    Requires the user to be logged in and the request to be POST.

    :param request: HttpRequest - The HTTP request object.
    :return: HttpResponse - The rendered 'profile' HTML page
    """

    uuid = get_user_from(request)
    user = get_user(User, uuid)

    updates = {
        'name': None,
        'surname': None,
        'email': None,
        'password': None,
        'image': None
    }

    for key in updates.keys():
        if not key in request.POST.keys():
            continue
        updates[key] = request.POST.get(key)

    updates = { k: v for k, v in updates.items() if v is not None }

    if img := request.FILES.get('image', None):
        updates['image'] = request.FILES.get('image')

    try:
        UserValidations(User, **updates).result()
    except ModelsAttributeError as e:
        return response_error(f'Could not update your account details: {e}')

    if img := updates.get('image', None):
        random_name = f"{uuid}{img.name[img.name.rfind('.'):]}"
        img.name = random_name
        user.image = img
    if name := updates.get('name', None):
        user.name = name
    if surname := updates.get('surname', None):
        user.surname = surname
    if email := updates.get('email', None):
        user.email = email
    if password := updates.get('password', None):
        user.password = password

    user.save()

    return response_success('Your account details has been updated successfully.')


@HANDLER.bind('logout', 'logout/', request='POST', session=True)
@requires_csrf_token
def logout(request): # Working view
    """
    Logs out the user flushing his session's data.
    Requires the request to be POST and the user to be logged in.

    :param request: HttpRequest - The HTTP request object.
    :return: HttpResponse - The rendered 'login' HTML page.
    """
    request.session.flush()
    return redirect(reverse('no_auth:login'))


@HANDLER.bind("profile", "account/", request='GET', session=True)
@requires_csrf_token
def profile(request):
    """
    Executes the query to retrieve user details after login.
    Requires the request to be GET and the user to be logged in.

    :param request: HttpRequest - The HTTP request object.
    :return: HttpResponse - The rendered HTML page with user details.
    """
    uuid = get_user_from(request)
    user = get_user(User, uuid)

    days_membership = no_timezone(user.date_joined)
    days_membership = (no_timezone(datetime.now()) - days_membership).days

    return render(request, "profile.html", {
        "user": user,
        "days_membership": days_membership
    })

