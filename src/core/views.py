from django.shortcuts import render

from Kanboard.settings import BASE_DIR
from core.models import Board
from static.services import RequestHandler, DBRequestBuilder, DBHybridTable as DHT, DBHybridField as DHF, JsonResponses
from django.contrib import messages

# Create your views here.
HANDLER = RequestHandler(BASE_DIR / 'db.sqlite3')

data = (
    DBRequestBuilder("user", "You are not logged!")\
    .select("username", "image")\
    .from_table("User")\
    .where(f"PARAM(uuid) = uuid"),
    DBRequestBuilder("boards_owned", "You do not own any board.")\
    .select(DHF("board", "id"),DHF("board", "name"),
        DHF("board", "description"),DHF("board", "image")
    )\
    .from_table(
        DHT("Board", "User",
            DHF("User", "uuid") == DHF("Board", "owner")
        )
    )\
    .where(f"PARAM(uuid) = {DHF('Board', 'owner')}"),
    DBRequestBuilder("boards_guest", "You are not a guest in any board.")\
    .select(DHF("board", "id"), DHF("board", "name"),
        DHF("board", "description"), DHF("board", "image")
    )\
    .from_table(
        DHT("Board", "Guests",
            DHF("Board", "id") == DHF("Guests", "board_id")
        )
    )\
    .where(f"PARAM(uuid) = {DHF('Guests', 'user_id')}")
)

@HANDLER.bind('dashboard', '/dashboard', *data)
def dashboard(request, user, boards_owned, boards_guested): # Display view
    user = request.session.get('uuid', None)
    if user is None:
        return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")

    class _Board:
        def __init__(self, id, name, description, image, owned=False):
            self.id = id
            self.name = name
            self.description = description
            self.image = image

    owned = [_Board(*board, owned=True) for board in boards_owned]
    guested = [_Board(*board) for board in boards_guested]

    return render(request, 'dashboard.html', {
        'user': user,
        'boards_owned': owned,
        'boards_guest': guested
    })


@HANDLER.bind('create_board', '/create_board')
def create_board(request): # Working view
    user = request.session.get('uuid', None)
    if user is None:
        return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")
    owner = user
    name = request.POST['name']
    description = request.POST['description']
    # to be completed


