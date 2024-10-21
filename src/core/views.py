from io import BytesIO

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.context_processors import request
from django.views.decorators.csrf import requires_csrf_token

from Kanboard.settings import BASE_DIR
from authentication.models import User
from core.models import Board, Column, Card, Guest
from static.services import RequestHandler, JsonResponses
from django.utils import timezone

from static.utils.utils import get_user_from, response_error, get_board, \
    check_user_not_owner_or_guest, check_user_invalid, check_board_invalid, \
    get_expired_cards_of_board, get_cards_of_board, response_success

# Create your views here.
HANDLER = RequestHandler()

@HANDLER.bind("board", "board/<int:board_id>", session=True, request="GET")
def board_view(request, board_id):

    uuid = get_user_from(request)
    board = get_board(Board, board_id)

    if check_board_invalid(board):
        return response_error("Board not found.")

    if check_user_not_owner_or_guest(Board, Guest, uuid, board_id):
        return response_error("You do not have access to this board.")

    board_info = {
        'id': board.id,
        'name': board.name,
        'description': board.description,
        'image': board.image,
        'creation_date': board.creation_date
    }

    return render(request, "boards.html", {
        "board": board_info
    })


@HANDLER.bind("columns", "columns/<int:board_id>", session=True, request="POST")
def columns_view(request, board_id):

    uuid = get_user_from(request)
    board = get_board(Board, board_id)

    if check_board_invalid(board):
        return response_error("Board not found.")

    if check_user_not_owner_or_guest(Board, Guest, uuid, board_id):
        return response_error("You do not have access to this board.")

    columns = Column.objects.filter(board_id=board_id).all()

    columns_info = [column for column in columns]

    return JsonResponse(columns_info, safe=False)

#
# data = (
#     DBRequestBuilder("column_details", "No column found with this ID!")
#     .select("id", "title", "description", "color", "index")
#     .from_table("columns")
#     .where("id = PARAM(column_id)"),
#
#     DBRequestBuilder("column_cards", "No cards found for this column!")
#     .select("id", "title", "description", "expiration_date")
#     .from_table("cards")
#     .where("column_id = PARAM(column_id)")
# )
#
#
# @HANDLER.bind("column_details", "<int:column_id>/column_details", *data)
# def column_details_view(request, column_id, column_details, column_cards):
#     """
# """    Executes the query to retrieve column details.
#
#     :param request: HttpRequest - The HTTP request object.
#     :param column_details: str - The result of the column details query.
#     :return: HttpResponse - The rendered HTML page with column details."""
# """
#
#     # Define an internal class to represent a card in the column
#     class _Card:
#         def __init__(self, card_data):
#             self.id = card_data["id"]
#             self.title = card_data["title"]
#             self.description = card_data["description"]
#             self.expiration_date = card_data["expiration_date"]
#             self.is_expired = self.check_if_expired()
#
#         # Method to check if the card is expired based on the current date and expiration date
#         def check_if_expired(self):
#             return timezone.now() > self.expiration_date if self.expiration_date else False
#
#     cards_column = [_Card(*card) for card in column_cards]
#
#     return render(request, "column_details.html", {
#         "column": column_details,
#         "cards_column": cards_column
#     })
#
#
# data = (
#     DBRequestBuilder("column_cards", "No cards found for this column!")
#     .select("id", "title", "description", "color", "creation_date", "expiration_date", "story_points", "index")
#     .from_table("cards")
#     .where("column_id = PARAM(column_id)"),
# )
#
#
# @HANDLER.bind("column_cards", "<int:column_id>/column_cards", *data)
# def column_cards_view(request, column_id, column_cards):
#     """
# """    Executes the query to retrieve the list of cards for a specific column.
#     :param request: HttpRequest - The HTTP request object.
#     :param column_cards: str - The result of the column cards query.
#     :return: HttpResponse - The rendered HTML page with the list of cards."""
# """
#     return render(request, "column_cards.html", {
#         "cards": list(column_cards)
#     })
#
#
# data = (
#     DBRequestBuilder("card_details", "No card found with this ID!")
#     .select("id", "title", "description", "color", "creation_date", "expiration_date", "story_points")
#     .from_table("cards")
#     .where("id = PARAM(card_id)"),
#
# )
#
#
# @HANDLER.bind("card_details", "<int:card_id>/card_details", *data)
# def card_detail_view(request, card_id, card_details):
#     """
# """    Executes the query to retrieve card details.
#     :param request: HttpRequest - The HTTP request object.
#     :param card_details: str - The result of the card details query.
#     :return: HttpResponse - The rendered HTML page with card details."""
# """
#
#     return render(request, "card_details.html", {
#         "card": card_details
#     })
#
#
# @HANDLER.bind("add_column", "<int:board_id>/add_column")  # Working view
# def add_column_view(request, board_id):
#     """
# """    Adds a new column to the specified board if the user is authenticated and is the owner of the board.
#     :param request: HttpRequest - The HTTP request object.
#     :param board_id: int - The ID of the board where the column will be added.
#     :param uuid: str - The UUID of the authenticated user passed by the RequestHandler.
#     :return: JsonResponse - The JSON response with the result of the operation."""
#    """
#
#     user = request.session.get('user_id', None)
#
#     if user is None:
#         return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")
#
#     try:
#         board = Board.objects.get(id=board_id)
#     except Board.DoesNotExist:
#         return JsonResponses.response(JsonResponses.ERROR, "Board not found")
#
#     if board.owner.uuid != user:
#         return JsonResponses.response(JsonResponses.ERROR, "You do not have permission to add a column to this board.")
#
#     if request.method != "POST":
#         return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")
#
#     title = request.POST.get("title")
#     color = request.POST.get("color")
#     description = request.POST.get("description")
#
#     try:
#         add_column_query = DBRequestBuilder("add_column", "Error while adding the column!")
#         add_column_query.insert("columns", "board_id", "title", "color", "description")
#         add_column_query.values(board_id, title, color, description)
#
#         db_service.execute(add_column_query.query())
#
#         return JsonResponses.response(JsonResponses.SUCCESS, "Column added successfully")
#     except Exception as e:
#         return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")
#
#
# @HANDLER.bind("delete_column", "<int:board_id>/<int:column_id>/delete_column")
# def delete_column_view(request, board_id, column_id):
#     """
#     Executes the query to delete a column from a board, but only if the current user is authenticated and is the owner of the board.
#     :param request: HttpRequest - The HTTP request object.
#     :param board_id: int - The ID of the board from which the column will be deleted.
#     :param column_id: int - The ID of the column to be deleted.
#     :return: JsonResponse - The JSON response with the result of the operation.
#     """
#
#     user = request.session.get('user_id', None)
#
#     if user is None:
#         return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")
#
#     try:
#         board = Board.objects.get(id=board_id)
#     except Board.DoesNotExist:
#         return JsonResponses.response(JsonResponses.ERROR, "Board not found")
#
#     if board.owner.uuid != user:
#         return JsonResponses.response(JsonResponses.ERROR,
#                                       "You do not have permission to delete a column from this board.")
#
#     if request.method != "POST":
#         return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")
#
#     try:
#         delete_column_query = DBRequestBuilder("delete_column", "Error while deleting the column!")
#         delete_column_query.complex(f"DELETE FROM columns WHERE id = {column_id} AND board_id = {board_id}")
#
#         db_service.execute(delete_column_query.query())
#
#         return JsonResponses.response(JsonResponses.SUCCESS, "Column deleted successfully")
#     except Exception as e:
#         return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")
#
#
# @HANDLER.bind("add_card", "<int:column_id>/add_card")
# def add_card_view(request, column_id):
#     """
#     Executes the query to add a new card to a column, but only if the current user is authenticated and is the owner of the board.
#     :param request: HttpRequest - The HTTP request object.
#     :param column_id: int - The ID of the column where the card will be added.
#     :return: JsonResponse - The JSON response with the result of the operation.
#     """
#
#     user = request.session.get('user_id', None)
#
#     if user is None:
#         return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")
#
#     try:
#         column = Column.objects.get(id=column_id)
#         board = column.board_id
#     except Column.DoesNotExist:
#         return JsonResponses.response(JsonResponses.ERROR, "Column not found")
#
#     if board.owner.uuid != user:
#         return JsonResponses.response(JsonResponses.ERROR, "You do not have permission to add a card to this column.")
#
#     if request.method != "POST":
#         return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")
#
#     title = request.POST.get("title")
#     description = request.POST.get("description")
#     color = request.POST.get("color")
#     expiration_date = request.POST.get("expiration_date")
#
#     try:
#         add_card_query = DBRequestBuilder("add_card", "Error while adding the card!")
#         add_card_query.insert("cards", "column_id", "title", "description", "color", "expiration_date")
#         add_card_query.values(column_id, title, description, color, expiration_date)
#
#         db_service.execute(add_card_query.query())
#
#         return JsonResponses.response(JsonResponses.SUCCESS, "Card added successfully")
#     except Exception as e:
#         return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")
#
#
# @HANDLER.bind("delete_card", "<int:column_id>/<int:card_id>/delete_card")
# def delete_card_view(request, column_id, card_id):
#     """
#     Executes the query to delete a card from a column, but only if the current user is authenticated and is the owner of the board.
#     :param request: HttpRequest - The HTTP request object.
#     :param column_id: int - The ID of the column from which the card will be deleted.
#     :param card_id: int - The ID of the card to be deleted.
#     :return: JsonResponse - The JSON response with the result of the operation.
#     """
#
#     user = request.session.get('user_id', None)
#
#     if user is None:
#         return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")
#
#     try:
#         column = Column.objects.get(id=column_id)
#         board = column.board_id
#     except Column.DoesNotExist:
#         return JsonResponses.response(JsonResponses.ERROR, "Column not found")
#
#     if board.owner != user:
#         return JsonResponses.response(JsonResponses.ERROR,
#                                       "You do not have permission to delete a card from this column.")
#
#     if request.method != "POST":
#         return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")
#
#     try:
#
#         delete_card_query = DBRequestBuilder("delete_card", "Error while deleting the card!")
#         delete_card_query.complex(f"DELETE FROM cards WHERE id = {card_id} AND column_id = {column_id}")
#
#         db_service.execute(delete_card_query.query())
#
#         return JsonResponses.response(JsonResponses.SUCCESS, "Card deleted successfully")
#     except Exception as e:
#         return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")
#
#
# @HANDLER.bind('update_column', '<int:board_id>/<int:column_id>/changes')
# def update_column_view(request, board_id, column_id):
#     """
#     Executes the query to delete a card from a column, but only if the current user is authenticated and is the owner of the board.
#
#     Parameters:
#     - request: HttpRequest object containing the request details.
#     - column_id: The ID of the column from which the card will be deleted.
#     - card_id: The ID of the card to be deleted.
#
#     Returns:
#     - JsonResponse: The JSON response containing the result of the operation.
#     """
#
#     column = Column.objects.filter(id=column_id, board_id=board_id).first()
#
#     if not column:
#         return JsonResponses.response(JsonResponses.ERROR, "Column not found.")
#
#     if request.method != "POST":
#         return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")
#
#     new_name = request.POST.get('title', None)
#
#     if not new_name:
#         return JsonResponses.response(JsonResponses.ERROR, "Column name cannot be empty.")
#
#     column.title = new_name
#
#     try:
#         column.save()
#
#         return JsonResponses.response(JsonResponses.SUCCESS, "Column name updated successfully.")
#     except Exception as e:
#         return JsonResponses.response(JsonResponses.ERROR, f"Error updating column name: {str(e)}")
#
#
# @HANDLER.bind('update_card', '<int:board_id>/<int:column_id>/<int:card_id>/changes')
# def update_card_view(request, board_id, column_id, card_id):
#     """
#     Updates the title, description, expiration date, story points, and column of a card, but only if the current user is authenticated and is the owner of the board.
#
#     Parameters:
#     - request: HttpRequest object containing the request details.
#     - board_id: The ID of the board to which the card belongs.
#     - column_id: The ID of the current column of the card.
#     - card_id: The ID of the card to be updated.
#
#     Returns:
#     - JsonResponse: The JSON response containing the result of the operation.
#     """
#
#     card = Card.objects.filter(id=card_id, board_id=board_id, column_id=column_id).first()
#
#     if not card:
#         return JsonResponses.response(JsonResponses.ERROR, "Card not found.")
#
#     if request.method != "POST":
#         return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")
#
#     updates = {
#         'title': None,
#         'description': None,
#         'expiration_date': None,
#         'story_points': None,
#         'column_id': None
#     }
#
#     for key in updates.keys():
#         if key in request.POST:
#             updates[key] = request.POST.get(key)
#
#     if updates['title']:
#         card.title = updates['title']
#
#     if updates['description']:
#         card.description = updates['description']
#
#     if updates['expiration_date']:
#         card.expiration_date = updates['expiration_date']
#
#     if updates['story_points']:
#         card.story_points = updates['story_points']
#
#     if updates['column_id']:
#         new_column = Column.objects.filter(id=updates['column_id'], board_id=board_id).first()
#         if not new_column:
#             return JsonResponses.response(JsonResponses.ERROR, "Column not found.")
#         card.column_id = new_column
#
#     try:
#         card.save()
#
#         return JsonResponses.response(JsonResponses.SUCCESS, "Card updated successfully.")
#     except Exception as e:
#         return JsonResponses.response(JsonResponses.ERROR, f"Error updating card: {str(e)}")
#
#
@HANDLER.bind("burndown", "burndown/<int:board_id>", request="GET", session=True)
def burndown_view(request, board_id):

    uuid = get_user_from(request)
    board = get_board(Board, board_id)

    if check_board_invalid(board):
        return response_error("Board not found.")

    if check_user_not_owner_or_guest(Board, Guest, uuid, board_id):
        return response_error("You do not have access to this board.")

    cards = get_cards_of_board(Card, board_id)
    expired_cards = get_expired_cards_of_board(Card, board_id)

    total_cards = cards.count()
    total_expired_cards = expired_cards.count()

    class TemplateColumn:
        def __init__(self, _column_title, _card_count):
            self.name = _column_title
            self.card_count = _card_count

    # column cards
    columns = Column.objects.filter(board_id=board_id)
    cards_per_column = []
    for column in columns:
        template_column = TemplateColumn(column.title, Card.objects.filter(column_id=column.id).count())
        cards_per_column.append(template_column)

    # story_points
    total_story_points = 0
    for card in cards:
        total_story_points += card.story_points

    return render(request, 'burndown.html', {
        'board': board,
        'total_cards': total_cards,
        'cards_per_column': cards_per_column,
        'expired_cards': total_expired_cards,
        'total_story_points': total_story_points
    })


@HANDLER.bind('dashboard', 'dashboard/', request='GET', session=True)
@requires_csrf_token
def dashboard(request):
    uuid = get_user_from(request)

    user = User.objects.filter(uuid=uuid).first()

    boards_owned = [board for board in Board.objects.filter(owner=uuid).all()]
    boards_guested = [board for board in Board.objects.all() if Guest.objects.filter(user_id=uuid, board_id=board.id).exists()]

    class TemplateBoard:
        def __init__(self, board):
            self.name = board.name
            self.description = board.description
            self.image = board.image
            self.id = board.id
            self.is_guest = board.owner != uuid

    boards_owned = [TemplateBoard(board) for board in boards_owned + boards_guested]

    return render(request, 'dashboard.html', {
        'user': user,
        'boards': boards_owned
    })


@HANDLER.bind("create_board", "dashboard/new_board/", session=True, request="POST")
def create_board_view(request):
    """
    Creates a new board for the logged-in user.
    :param request: HttpRequest - The HTTP request object.
    :param uuid: str - The UUID of the authenticated user passed by the RequestHandler.
    :return: JsonResponse - The JSON response with the result of the operation.
    """

    user = get_user_from(request)

    print(request.POST)

    name = request.POST.get("board_title")
    description = request.POST.get("board_description")

    if not name or not description:
        return response_error("Name and description are required.")

    try:
        new_board = Board.objects.create(
            owner_id=user,
            name=name,
            description=description,
            creation_date=timezone.now()
        )
        new_board.save()
    except Exception as e:
        return response_error(f"Couldn't create the board: {e}")

    return redirect('core:board', board_id=new_board.id)


# @HANDLER.bind("add_user", "board/<int:board_id>/add_user/")
# def add_user_view(request, board_id):
#     """
#     Executes the query to add a user to a board using the username, but only if the current user is authenticated and is the owner of the board.
#     :param request: HttpRequest - The HTTP request object.
#     :param board_id: int - The ID of the board where the user will be added.
#     :return: JsonResponse - The JSON response with the result of the operation.
#     """
#
#     user = request.session.get('user_id', None)
#     if user is None:
#         return JsonResponses.response(JsonResponses.ERROR, "You are not logged.")
#
#     if request.method != "POST":
#         return JsonResponses.response(JsonResponses.ERROR, "Invalid request method.")
#
#     try:
#         board = Board.objects.get(id=board_id)
#     except Board.DoesNotExist:
#         return JsonResponses.response(JsonResponses.ERROR, "Board not found.")
#
#     if board.owner != user:
#         return JsonResponses.response(JsonResponses.ERROR, "You do not have permission to add a user to this board.")
#
#     username_to_add = request.POST.get("username")
#
#     try:
#         find_user_query = DBRequestBuilder("find_user", "User not found!")
#         (find_user_query.select("uuid").from_table("user").where(f"username = {username_to_add}"))
#
#         user_to_add = db_service.execute(find_user_query.query())
#
#         if not user_to_add:
#             return JsonResponses.response(JsonResponses.ERROR, "User not found.")
#         user_to_add_id = user_to_add[0][0]
#     except Exception as e:
#         return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")
#
#     try:
#         check_membership_query = DBRequestBuilder("check_membership", "Error checking membership!")
#         check_membership_query.select("id").from_table("guests").where(f"user_id = {user_to_add_id} AND board_id = {board_id}")
#         existing_member = db_service.execute(check_membership_query.query())
#
#         if existing_member:
#             return JsonResponses.response(JsonResponses.ERROR, "User is already a member of this board.")
#     except Exception as e:
#         return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")
#
#     try:
#         add_user_query = DBRequestBuilder("add_user", "Error while adding the user to the board!")
#         add_user_query.insert("guests", "user_id", "board_id") \
#                         .values(user_to_add_id, board_id)
#
#         db_service.execute(add_user_query.query())
#
#         return JsonResponses.response(JsonResponses.SUCCESS, f"User {username_to_add} added to the board.")
#     except Exception as e:
#         return JsonResponses.response(JsonResponses.ERROR, f"Error: {e}")
#
#

@HANDLER.bind("remove_user", "board/<int:board_id>/remove_user/", request="POST", session=True)
@requires_csrf_token
def remove_user_view(request, board_id):
    """
    Executes the query to remove a user from a board using the username, but only if the current user is authenticated
    and is the owner of the board.
    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board from which the user will be removed.
    :return: JsonResponse - The JSON response with the result of the operation.
    """

    uuid = get_user_from(request)

    if not Board.objects.filter(id=board_id, owner=uuid).exists():
        response_error("You don't own this board.")

    username_to_remove = request.POST.get("username")

    try:
        uuid = str(User.objects.filter(username=username_to_remove).first().uuid)
        if guest := Guest.objects.filter(user_id=uuid, board_id=board_id).first():
            guest.delete()
    except Exception as e:
        return response_error(f"Error: {e}")

    return response_success(f"{username_to_remove} has been removed successfully from this board.")


@HANDLER.bind("burndown_image", "burndown/<int:board_id>/image", request="GET", session=True)
@requires_csrf_token
def burndown_image_view(request, board_id):

    uuid = get_user_from(request)
    board = get_board(Board, board_id)

    if not board:
        response_error("Board not found.")

    if check_user_not_owner_or_guest(Board, Guest, uuid, board_id):
        response_error("You do not have access to this board.")

    total_cards = get_cards_of_board(Card, board_id).count()
    expired_cards = get_expired_cards_of_board(Card, board_id).count()

    def generate_burndown_image(cards, exp_cards):
        import matplotlib.pyplot as plt

        labels = ['Cards', 'Expired Cards']
        sizes = [cards, exp_cards]
        colors = ['#66b3ff', '#ff9999']
        explode = (0.05, 0)

        def func(pct, allvalues):
            absolute = int(pct / 100. * sum(allvalues))
            return f"{pct:.1f}%\n({absolute})"

        plt.figure(figsize=(7, 7), facecolor='#0f0f18')

        wedges, texts, autotexts = plt.pie(sizes,
                                           explode=explode,
                                           labels=labels,
                                           colors=colors,
                                           autopct=lambda pct: func(pct, sizes),
                                           pctdistance=0.75,
                                           shadow=True,
                                           startangle=140,
                                           textprops={'fontweight': 'bold'})

        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')

        for text in texts:
            text.set_color('white')
            text.set_fontweight('bold')

        plt.title('Card Graph', color='white', fontweight='bold')

        plt.gca().set_facecolor('#0f0f18')

        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='#0f0f18')
        buffer.seek(0)

        return HttpResponse(buffer, content_type='image/png')

    return generate_burndown_image(total_cards - expired_cards, expired_cards)


@HANDLER.bind("board_creation", "dashboard/creation/", request="GET", session=True)
def modal_board_creation(request):
    modal = """
        <div class="form-box" style="width: 100%; height: 100%; border-radius: 8px;">
            <h1 class="form-title">Create a new board</h1>
            <div class="input-container">
                <img src="../../static/assets/icons/tag.svg" alt="Repeat Password Icon" class="input-icon">
                <input type="text" class="input-field" id="board_title" name="board_title" placeholder="Board title" required>
            </div>
            <div class="input-container">
                <img src="../../static/assets/icons/description.svg" alt="Repeat Password Icon" class="input-icon">
                <textarea class="input-field" id="board_description" name="board_description" maxlength="256" rows="4" placeholder="Board description" required></textarea>
            </div>
            <button type="submit" class="button submit-button" id="create">Create</button>
            <script>
                document.querySelector("#create").addEventListener("click", () => {
                    triggerMicro('new_board/', ['board_title', 'board_description'], displayMessage, displayMessage); 
                });
            </script>
        </div>
    """
    return HttpResponse(modal)

