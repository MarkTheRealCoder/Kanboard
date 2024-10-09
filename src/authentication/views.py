from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Kanboard.settings import BASE_DIR
from static.services import RequestHandler, ModelsAttributeError, UserValidations, JsonResponses
from .models import User
import re



HANDLER = RequestHandler(BASE_DIR / 'db.sqlite3')


@HANDLER.bind('user_management', 'account/changes')
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


@HANDLER.bind('logout', 'logout')
def logout(request):
    request.session.flush()
    return redirect('index')


@HANDLER.bind("registration_submission", "register/submit/")
def registration_submission(request): # Working view
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Verifica se l'utente esiste già
        if User.objects.filter(username=username).exists():
            return JsonResponses.response(JsonResponses.ERROR, "Username Already Used")

        if User.objects.filter(email=email).exists():
            return JsonResponses.response(JsonResponses.ERROR, "Email Already Used")

        # Crea il nuovo utente
        user = User.objects.create_user(username=username, email=email, password=password)

        return redirect('login')  # Reindirizza alla pagina di login

    return render(request, 'registration.html')

@HANDLER.bind("login_submission", "login/submit/")
def login_submission(request): # Working view
    key = request.POST['key']
    password = request.POST['password']
    # Controlla se la key è un'email usando una regex
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    field = "email" if re.match(email_regex, key) else "username"
    request = {field: key, "password":password}
    user = User.objects.filter(**request).exists()  # Usa .filter() e ottieni il primo risultato

    if not user:
        return JsonResponses.response(JsonResponses.ERROR, "Username o password non corretti")

    return redirect(reverse('no_auth:index'))