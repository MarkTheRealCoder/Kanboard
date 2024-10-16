from django.shortcuts import render

from Kanboard.settings import BASE_DIR
from core.models import Board, Column, Card
from static.services import RequestHandler, DBRequestBuilder, DBHybridTable as DHT, DBHybridField as DHF, JsonResponses
from static.services.database import _DBServices
from django.contrib import messages
from django.utils import timezone

# Create your views here.
HANDLER = RequestHandler(BASE_DIR / 'db.sqlite3')

#*** TODO
db_service = _DBServices(BASE_DIR / 'db.sqlite3')

data = (
    DBRequestBuilder("board_details", "No board found with this ID!")
    .select("id", "name", "description", "image", "creation_date")
    .from_table("boards")
    .where("id = PARAM(board_id)"),
)


@HANDLER.bind("board_details", "<int:board_id>/board_details", *data)
def board_details_view(request, board_id, board_details):
    """
    Executes the query to retrieve board details.
    :param request: HttpRequest - The HTTP request object.
    :param board_details: str - The result of the board details query.
    :return: HttpResponse - The rendered HTML page with board details.
    """
    return render(request, "board_details.html", {
        "board": board_details
    })


data = (
    DBRequestBuilder("board_columns", "No columns found for this board!")
    .select("id", "title", "color", "description", "index")
    .from_table("columns")
    .where("board_id = PARAM(board_id)"),
)


@HANDLER.bind("board_columns", "<int:board_id>/board_columns", *data)
def board_columns_view(request, board_id, board_columns):
    """
    Executes the query to retrieve the columns of a specific board.

    Parameters:
    - request: HttpRequest object containing the request details.
    - board_id: The ID of the board whose columns will be retrieved.
    - board_columns: The result of the board columns query.

    Returns:
    - HttpResponse: The rendered HTML page with the list of columns.
    """
    return render(request, "board_columns.html", {
        "columns": board_columns
    })


data = (
    DBRequestBuilder("column_details", "No column found with this ID!")
    .select("id", "title", "description", "color", "index")
    .from_table("columns")
    .where("id = PARAM(column_id)"),

    DBRequestBuilder("column_cards", "No cards found for this column!")
    .select("id", "title", "description", "expiration_date")
    .from_table("cards")
    .where("column_id = PARAM(column_id)")
)


@HANDLER.bind("column_details", "<int:column_id>/column_details", *data)
def column_details_view(request, column_id, column_details, column_cards):
    """
    Executes the query to retrieve column details.

    :param request: HttpRequest - The HTTP request object.
    :param column_details: str - The result of the column details query.
    :return: HttpResponse - The rendered HTML page with column details.
    """

    # Define an internal class to represent a card in the column
    class _Card:
        def __init__(self, card_data):
            self.id = card_data["id"]
            self.title = card_data["title"]
            self.description = card_data["description"]
            self.expiration_date = card_data["expiration_date"]
            self.is_expired = self.check_if_expired()

        # Method to check if the card is expired based on the current date and expiration date
        def check_if_expired(self):
            return timezone.now() > self.expiration_date if self.expiration_date else False

    cards_column = [_Card(*card) for card in column_cards]

    return render(request, "column_details.html", {
        "column": column_details,
        "cards_column": cards_column
    })


data = (
    DBRequestBuilder("column_cards", "No cards found for this column!")
    .select("id", "title", "description", "color", "creation_date", "expiration_date", "story_points", "index")
    .from_table("cards")
    .where("column_id = PARAM(column_id)"),
)


@HANDLER.bind("column_cards", "<int:column_id>/column_cards", *data)
def column_cards_view(request, column_id, column_cards):
    """
    Executes the query to retrieve the list of cards for a specific column.
    :param request: HttpRequest - The HTTP request object.
    :param column_cards: str - The result of the column cards query.
    :return: HttpResponse - The rendered HTML page with the list of cards.
    """
    return render(request, "column_cards.html", {
        "cards": list(column_cards)
    })


data = (
    DBRequestBuilder("card_details", "No card found with this ID!")
    .select("id", "title", "description", "color", "creation_date", "expiration_date", "story_points")
    .from_table("cards")
    .where("id = PARAM(card_id)"),

)


@HANDLER.bind("card_details", "<int:card_id>/card_details", *data)
def card_detail_view(request, card_id, card_details):
    """
    Executes the query to retrieve card details.
    :param request: HttpRequest - The HTTP request object.
    :param card_details: str - The result of the card details query.
    :return: HttpResponse - The rendered HTML page with card details.
    """

    return render(request, "card_details.html", {
        "card": card_details
    })


@HANDLER.bind("add_column", "<int:board_id>/add_column")  # Working view
def add_column_view(request, board_id):
    """
    Adds a new column to the specified board if the user is authenticated and is the owner of the board.
    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board where the column will be added.
    :param uuid: str - The UUID of the authenticated user passed by the RequestHandler.
    :return: JsonResponse - The JSON response with the result of the operation.
    """

    user = request.session.get('user_id', None)

    if user is None:
        return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")

    try:
        board = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        return JsonResponses.response(JsonResponses.ERROR, "Board not found")

    if board.owner.uuid != user:
        return JsonResponses.response(JsonResponses.ERROR, "You do not have permission to add a column to this board.")

    if request.method != "POST":
        return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")

    title = request.POST.get("title")
    color = request.POST.get("color")
    description = request.POST.get("description")

    try:
        add_column_query = DBRequestBuilder("add_column", "Error while adding the column!")
        add_column_query.insert("columns", "board_id", "title", "color", "description")
        add_column_query.values(board_id, title, color, description)

        db_service.execute(add_column_query.query())

        return JsonResponses.response(JsonResponses.SUCCESS, "Column added successfully")
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")


@HANDLER.bind("delete_column", "<int:board_id>/<int:column_id>/delete_column")
def delete_column_view(request, board_id, column_id):
    """
    Executes the query to delete a column from a board, but only if the current user is authenticated and is the owner of the board.
    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board from which the column will be deleted.
    :param column_id: int - The ID of the column to be deleted.
    :return: JsonResponse - The JSON response with the result of the operation.
    """

    user = request.session.get('user_id', None)

    if user is None:
        return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")

    try:
        board = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        return JsonResponses.response(JsonResponses.ERROR, "Board not found")

    if board.owner.uuid != user:
        return JsonResponses.response(JsonResponses.ERROR,
                                      "You do not have permission to delete a column from this board.")

    if request.method != "POST":
        return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")

    try:
        delete_column_query = DBRequestBuilder("delete_column", "Error while deleting the column!")
        delete_column_query.complex(f"DELETE FROM columns WHERE id = {column_id} AND board_id = {board_id}")

        db_service.execute(delete_column_query.query())

        return JsonResponses.response(JsonResponses.SUCCESS, "Column deleted successfully")
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")


@HANDLER.bind("add_card", "<int:column_id>/add_card")
def add_card_view(request, column_id):
    """
    Executes the query to add a new card to a column, but only if the current user is authenticated and is the owner of the board.
    :param request: HttpRequest - The HTTP request object.
    :param column_id: int - The ID of the column where the card will be added.
    :return: JsonResponse - The JSON response with the result of the operation.
    """

    user = request.session.get('user_id', None)

    if user is None:
        return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")

    try:
        column = Column.objects.get(id=column_id)
        board = column.board_id
    except Column.DoesNotExist:
        return JsonResponses.response(JsonResponses.ERROR, "Column not found")

    if board.owner.uuid != user:
        return JsonResponses.response(JsonResponses.ERROR, "You do not have permission to add a card to this column.")

    if request.method != "POST":
        return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")

    title = request.POST.get("title")
    description = request.POST.get("description")
    color = request.POST.get("color")
    expiration_date = request.POST.get("expiration_date")

    try:
        add_card_query = DBRequestBuilder("add_card", "Error while adding the card!")
        add_card_query.insert("cards", "column_id", "title", "description", "color", "expiration_date")
        add_card_query.values(column_id, title, description, color, expiration_date)

        db_service.execute(add_card_query.query())

        return JsonResponses.response(JsonResponses.SUCCESS, "Card added successfully")
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")


@HANDLER.bind("delete_card", "<int:column_id>/<int:card_id>/delete_card")
def delete_card_view(request, column_id, card_id):
    """
    Executes the query to delete a card from a column, but only if the current user is authenticated and is the owner of the board.
    :param request: HttpRequest - The HTTP request object.
    :param column_id: int - The ID of the column from which the card will be deleted.
    :param card_id: int - The ID of the card to be deleted.
    :return: JsonResponse - The JSON response with the result of the operation.
    """

    user = request.session.get('user_id', None)

    if user is None:
        return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")

    try:
        column = Column.objects.get(id=column_id)
        board = column.board_id
    except Column.DoesNotExist:
        return JsonResponses.response(JsonResponses.ERROR, "Column not found")

    if board.owner != user:
        return JsonResponses.response(JsonResponses.ERROR,
                                      "You do not have permission to delete a card from this column.")

    if request.method != "POST":
        return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")

    try:

        delete_card_query = DBRequestBuilder("delete_card", "Error while deleting the card!")
        delete_card_query.complex(f"DELETE FROM cards WHERE id = {card_id} AND column_id = {column_id}")

        db_service.execute(delete_card_query.query())

        return JsonResponses.response(JsonResponses.SUCCESS, "Card deleted successfully")
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")


@HANDLER.bind('update_column', '<int:board_id>/<int:column_id>/changes')
def update_column_view(request, board_id, column_id):
    """
    Executes the query to delete a card from a column, but only if the current user is authenticated and is the owner of the board.

    Parameters:
    - request: HttpRequest object containing the request details.
    - column_id: The ID of the column from which the card will be deleted.
    - card_id: The ID of the card to be deleted.

    Returns:
    - JsonResponse: The JSON response containing the result of the operation.
    """

    column = Column.objects.filter(id=column_id, board_id=board_id).first()

    if not column:
        return JsonResponses.response(JsonResponses.ERROR, "Column not found.")

    if request.method != "POST":
        return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")

    new_name = request.POST.get('title', None)

    if not new_name:
        return JsonResponses.response(JsonResponses.ERROR, "Column name cannot be empty.")

    column.title = new_name

    try:
        column.save()

        return JsonResponses.response(JsonResponses.SUCCESS, "Column name updated successfully.")
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error updating column name: {str(e)}")


@HANDLER.bind('update_card', '<int:board_id>/<int:column_id>/<int:card_id>/changes')
def update_card_view(request, board_id, column_id, card_id):
    """
    Updates the title, description, expiration date, story points, and column of a card, but only if the current user is authenticated and is the owner of the board.

    Parameters:
    - request: HttpRequest object containing the request details.
    - board_id: The ID of the board to which the card belongs.
    - column_id: The ID of the current column of the card.
    - card_id: The ID of the card to be updated.

    Returns:
    - JsonResponse: The JSON response containing the result of the operation.
    """

    card = Card.objects.filter(id=card_id, board_id=board_id, column_id=column_id).first()

    if not card:
        return JsonResponses.response(JsonResponses.ERROR, "Card not found.")

    if request.method != "POST":
        return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")

    updates = {
        'title': None,
        'description': None,
        'expiration_date': None,
        'story_points': None,
        'column_id': None
    }

    for key in updates.keys():
        if key in request.POST:
            updates[key] = request.POST.get(key)

    if updates['title']:
        card.title = updates['title']

    if updates['description']:
        card.description = updates['description']

    if updates['expiration_date']:
        card.expiration_date = updates['expiration_date']

    if updates['story_points']:
        card.story_points = updates['story_points']

    if updates['column_id']:
        new_column = Column.objects.filter(id=updates['column_id'], board_id=board_id).first()
        if not new_column:
            return JsonResponses.response(JsonResponses.ERROR, "Column not found.")
        card.column_id = new_column

    try:
        card.save()

        return JsonResponses.response(JsonResponses.SUCCESS, "Card updated successfully.")
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error updating card: {str(e)}")


@HANDLER.bind("burndown", "board/<int:board_id>/burndown/")
def burndown_view(request, board_id):
    user = request.session.get('user_id', None)

    if user is None:
        return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")

    board = Board.objects.filter(id=board_id).first()

    if not board:
        return JsonResponses.response(JsonResponses.ERROR, "Board not found.")

    # user must be owner or guest
    if board.owner_id != user and not board.guests_set.filter(user_id=user).exists():
        return JsonResponses.response(JsonResponses.ERROR, "You do not have access to this board.")

    # board cards
    total_cards = Card.objects.filter(board_id=board_id).count()

    # column cards
    columns = Column.objects.filter(board_id=board_id)
    cards_per_column = {}
    for column in columns:
        cards_per_column[column.title] = Card.objects.filter(column_id=column.id).count()

    # expired cards, expired_date less than timezone.now
    expired_cards = Card.objects.filter(board_id=board_id, expiration_date__lt=timezone.now()).count()

    # story_points
    total_story_points = 0
    cards = Card.objects.filter(board_id=board_id)
    for card in cards:
        total_story_points += card.story_points

    # Renderizza la pagina burndown
    return render(request, 'burndown.html', {
        'board': board,
        'total_cards': total_cards,
        'cards_per_column': cards_per_column,
        'expired_cards': expired_cards,
        'total_story_points': total_story_points
    })


data = (
    DBRequestBuilder("user", "You are not logged!")
    .select("username", "image")
    .from_table("User")
    .where(f"PARAM(uuid) = uuid"),

    DBRequestBuilder("boards_owned", "You do not own any board.")
    .select(
        DHF("board", "id"),
        DHF("board", "name"),
        DHF("board", "description"),
        DHF("board", "image")
    )
    .from_table(
        DHT("Board", "User",
            DHF("User", "uuid") == DHF("Board", "owner")
            )
    )
    .where(f"PARAM(uuid) = {DHF('Board', 'owner')}"),

    DBRequestBuilder("boards_guest", "You are not a guest in any board.")
    .select(
        DHF("board", "id"),
        DHF("board", "name"),
        DHF("board", "description"),
        DHF("board", "image")
    )
    .from_table(
        DHT("Board", "Guests",
            DHF("Board", "id") == DHF("Guests", "board_id")
            )
    )
    .where(f"PARAM(uuid) = {DHF('Guests', 'user_id')}")
)


@HANDLER.bind('dashboard', 'dashboard/', *data)
def dashboard(request, user, boards_owned, boards_guested):  # Display view
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


@HANDLER.bind("create_board", "board/create/")
def create_board_view(request):
    """
    Creates a new board for the logged-in user.
    :param request: HttpRequest - The HTTP request object.
    :param uuid: str - The UUID of the authenticated user passed by the RequestHandler.
    :return: JsonResponse - The JSON response with the result of the operation.
    """

    user = request.session.get('user_id', None)

    if user is None:
        return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")

    if request.method != "POST":
        return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")

    name = request.POST.get("name")
    description = request.POST.get("description")

    if not name or not description:
        return JsonResponses.response(JsonResponses.ERROR, "Name and description are required.")

    try:
        new_board = Board.objects.create(
            owner_id=user,
            name=name,
            description=description,
        )
        new_board.save()

        return JsonResponses.response(JsonResponses.SUCCESS, "Board created successfully.")
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")


@HANDLER.bind("add_user", "board/<int:board_id>/add_user/")
def add_user_view(request, board_id):
    """
    Executes the query to add a user to a board using the username, but only if the current user is authenticated and is the owner of the board.
    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board where the user will be added.
    :return: JsonResponse - The JSON response with the result of the operation.
    """

    user = request.session.get('user_id', None)
    if user is None:
        return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")

    if request.method != "POST":
        return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")

    try:
        board = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        return JsonResponses.response(JsonResponses.ERROR, "Board not found.")

    if board.owner != user:
        return JsonResponses.response(JsonResponses.ERROR, "You do not have permission to add a user to this board.")

    username_to_add = request.POST.get("username")

    try:
        find_user_query = DBRequestBuilder("find_user", "User not found!")
        (find_user_query.select("uuid").from_table("user").where(f"username = {username_to_add}"))

        user_to_add = db_service.execute(find_user_query.query())

        if not user_to_add:
            return JsonResponses.response(JsonResponses.ERROR, "User not found.")
        user_to_add_id = user_to_add[0][0]
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")

    try:
        check_membership_query = DBRequestBuilder("check_membership", "Error checking membership!")
        check_membership_query.select("id").from_table("guests").where(f"user_id = {user_to_add_id} AND board_id = {board_id}")
        existing_member = db_service.execute(check_membership_query.query())

        if existing_member:
            return JsonResponses.response(JsonResponses.ERROR, "User is already a member of this board.")
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")

    try:
        add_user_query = DBRequestBuilder("add_user", "Error while adding the user to the board!")
        add_user_query.insert("guests", "user_id", "board_id")
        add_user_query.values(user_to_add_id, board_id)

        db_service.execute(add_user_query.query())

        return JsonResponses.response(JsonResponses.SUCCESS, f"User {username_to_add} added to the board.")
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")


@HANDLER.bind("remove_user", "board/<int:board_id>/remove_user/")
def remove_user_view(request, board_id):
    """
    Executes the query to remove a user from a board using the username, but only if the current user is authenticated and is the owner of the board.
    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board from which the user will be removed.
    :return: JsonResponse - The JSON response with the result of the operation.
    """

    user = request.session.get('user_id', None)
    if user is None:
        return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")

    if request.method != "POST":
        return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")

    try:
        board = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        return JsonResponses.response(JsonResponses.ERROR, "Board not found.")

    if board.owner.uuid != user:
        return JsonResponses.response(JsonResponses.ERROR,
                                      "You do not have permission to remove a user from this board.")

    username_to_remove = request.POST.get("username")

    try:
        find_user_query = DBRequestBuilder("find_user", "User not found!")
        (find_user_query.select("uuid").from_table("user").where(f"username = {username_to_remove}"))

        user_to_remove = db_service.execute(find_user_query.query())

        if not user_to_remove:
            return JsonResponses.response(JsonResponses.ERROR, "User not found.")
        user_to_remove_id = user_to_remove[0][0]
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")

    try:
        check_membership_query = DBRequestBuilder("check_membership", "Error checking membership!")
        check_membership_query.select("id").from_table("guests").where(f"user_id = {user_to_remove_id} AND board_id = {board_id}")
        existing_member = db_service.execute(check_membership_query.query())

        if not existing_member:
            return JsonResponses.response(JsonResponses.ERROR, "User is not a member of this board.")
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")

    try:
        remove_user_query = DBRequestBuilder("remove_user", "Error while removing the user from the board!")
        remove_user_query.complex(f"DELETE FROM guests WHERE user_id = {user_to_remove_id} AND board_id = {board_id}")

        db_service.execute(remove_user_query.query())

        return JsonResponses.response(JsonResponses.SUCCESS, f"User {username_to_remove} removed from the board.")
    except Exception as e:
        return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")

