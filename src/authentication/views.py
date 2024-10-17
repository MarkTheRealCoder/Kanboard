from datetime import timezone

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import requires_csrf_token
from django.utils import timezone

from Kanboard.settings import BASE_DIR

from static.services import RequestHandler, ModelsAttributeError, UserValidations, JsonResponses, DBQuery, DBTable
from static.utils.utils import response_error, get_user_from, response_success
from .models import User

# Create your views here.

HANDLER = RequestHandler(BASE_DIR / 'db.sqlite3')


@HANDLER.bind("registration_submission", "register/submit/", request="POST", session=False)
@requires_csrf_token
def registration_submission(request):

    required_fields = {
        'name': request.POST.get('name', None),
        'surname': request.POST.get('surname', None),
        'username': request.POST.get('username', None),
        'email': request.POST.get('email', None),
        'password': request.POST.get('password', None),
        'date_joined': timezone.now(),
        'last_login': timezone.now()
    }

    try:
        uuid = str(UserValidations(User, **required_fields).result().generate_uuid())
    except ModelsAttributeError as e:
        return JsonResponses.response(JsonResponses.ERROR, f'Something went wrong:\n{str(e)}.')

    User.objects.create(uuid=uuid, **required_fields).save()

    request.session['uuid'] = uuid
    request.session.set_expiry(0)

    print("Registered user")
    print("\tUUID:", uuid)
    print("\tUsername:", required_fields['username'])
    print("\tEmail:", required_fields['email'])
    print("\tName:", required_fields['name'])
    print("\tSurname:", required_fields['surname'])
    print("\tPassword:", required_fields['password'])

    return redirect(reverse('core:dashboard'))


@HANDLER.bind("login_submission", "login/submit/", request="POST", session=False)
@requires_csrf_token
def login_submission(request):

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

    to_filter = { field: key, "password":password }
    user = User.objects.filter(**to_filter).first()

    if not user:
        return response_error(f"{field.title()} or password are incorrect.")

    request.session['uuid'] = str(user.uuid)
    request.session.set_expiry(0)

    return redirect(reverse('core:dashboard'))


@HANDLER.bind('user_management', 'account/changes/', request="POST", session=True)
def user_management(request):

    uuid = get_user_from(request)

    updates = {
        'name': None,
        'surname': None,
        'email': None,
        'password': None,
        'image': None
    }

    for key in updates.keys():
        if not key in request.POST.keys():
            updates.pop(key)
            continue
        updates[key] = request.POST.get(key)

    if img := request.FILES.get('image', None):
        updates['image'] = request.FILES.get('image')

    try:
        user = User.objects.filter(uuid=uuid).first()

        UserValidations(User, **updates).result()

        if img := updates.get('image', None):
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
    except ModelsAttributeError:
        return response_error('Could not update your account details.')

    return response_success('Your account details has been updated successfully.')


@HANDLER.bind('logout', 'logout/', request='POST', session=True)
@requires_csrf_token
def logout(request): # Working view
    request.session.flush()
    return redirect(reverse('no_auth:index'))


queries = (
    DBQuery("user", "You are not logged in.")
        .filter(_user_uuid="PARAM(uuid)")
        .from_table(DBTable("User")),
)

@HANDLER.bind("user_details", "account/", *queries, request='GET', session=True)
@requires_csrf_token
def user_details_view(request, user):
    """
    Executes the query to retrieve user details after login.
    :param request: HttpRequest - The HTTP request object.
    :return: HttpResponse - The rendered HTML page with user details.
    """

    if not user:
        return response_error("No user found with this ID!")

    return render(request, "user_details.html", {
        "user": user
    })

