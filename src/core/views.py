import json
from datetime import datetime
from io import BytesIO
from uuid import uuid4

from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import requires_csrf_token

from authentication.models import User
from core.models import Board, Column, Card, Guest, Assignee
from static.services import RequestHandler, ColumnValidations, BoardValidations, ModelsAttributeError, CardValidations
from static.utils.utils import get_user_from, response_error, get_board, check_board_invalid, \
    check_user_not_owner_or_guest, no_timezone, get_cards_of_board, get_expired_cards_of_board, get_user, \
    check_user_not_owner, response_success, get_guest, get_columns, get_boards_owned, check_user_not_guest, \
    get_board_elements



# Create your views here.
HANDLER = RequestHandler()


@HANDLER.bind('dashboard', 'dashboard/', request='GET', session=True)
@requires_csrf_token
def dashboard(request):
    """
    Renders the dashboard page with the user details and boards.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :return: HttpResponse - The rendered HTML page with the user details and boards.
    """
    uuid = get_user_from(request)
    user = get_user(User, uuid)

    boards_owned = [board for board in get_boards_owned(Board, uuid)]
    boards_guested = [board for board in Board.objects.all() if not check_user_not_guest(Guest, board.id, uuid)]

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


@HANDLER.bind("board", "board/<int:board_id>/", request="GET", session=True)
@requires_csrf_token
def board(request, board_id):
    """
    Renders the board page with the board details and columns.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board to display.
    :return: HttpResponse - The rendered HTML page with the board details.
    """
    uuid = get_user_from(request)
    board = get_board(Board, board_id)

    if check_board_invalid(board):
        return response_error("Board not found.")

    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You do not have access to this board.")

    board_info = {
        'id': board.id,
        'name': board.name,
        'description': board.description,
        'image': board.image,
        'creation_date': board.creation_date
    }

    columns = get_board_elements(Column, Card, Assignee, User, board_id)
    return render(request, "boards.html", {
        "board": board_info,
        "columns": columns
    })


@HANDLER.bind("burndown", "burndown/<int:board_id>/", request="GET", session=True)
@requires_csrf_token
def burndown_view(request, board_id):
    """
    Renders the burndown chart page with the board details.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board to display.
    :return: HttpResponse - The rendered HTML page with the burndown chart.
    """
    uuid = get_user_from(request)
    board = get_board(Board, board_id)

    if check_board_invalid(board):
        return response_error("Board not found.")

    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You do not have access to this board.")

    class TemplateColumn:
        def __init__(self, _column):
            nonlocal board
            self.name = _column.title
            cards = Card.objects.filter(column_id=_column, board_id=board)
            self.active_cards = cards.filter(expiration_date__gt=no_timezone(datetime.now()), completion_date__isnull=True).count() \
                                + cards.filter(expiration_date__isnull=True).count()
            self.expired_cards = cards.filter(expiration_date__lt=no_timezone(datetime.now()), completion_date__isnull=True).count()
            self.completed_cards = cards.filter(completion_date__isnull=False).count()
            self.total_cards = cards.count()
            self.story_points = cards.aggregate(total_story_points=Coalesce(Sum(F('story_points')), Value(0)))['total_story_points']

    # column cards
    columns = get_columns(Column, board_id)
    columns = [TemplateColumn(column) for column in columns]
    total_cards = sum([column.total_cards for column in columns])
    total_active_cards = sum([column.active_cards for column in columns])
    total_expired_cards = sum([column.expired_cards for column in columns])
    total_completed_cards = sum([column.completed_cards for column in columns])
    total_story_points = sum([column.story_points for column in columns])

    return render(request, 'burndown.html', {
        'board': board,
        'columns': columns,
        'total_active_cards': total_active_cards,
        'total_expired_cards': total_expired_cards,
        'total_completed_cards': total_completed_cards,
        'total_cards': total_cards,
        'total_story_points': total_story_points,
    })


@HANDLER.bind("burndown_image", "burndown/<int:board_id>/image/", request="GET", session=True)
@requires_csrf_token
def burndown_image_view(request, board_id):
    """
    Generates a burndown image for the specified board.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board to generate the burndown image.
    :return: HttpResponse - The image response with the burndown chart.
    """
    uuid = get_user_from(request)
    board = get_board(Board, board_id)

    if not board:
        response_error("Board not found.")

    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
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


@HANDLER.bind("new_board", "dashboard/new/board/", request="POST", session=True)
@requires_csrf_token
def new_board(request):
    """
    Renders the create board page with the user details.
    Requires the method to be POST and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :return: JsonResponse - The JSON response with the result of the operation.
    """
    uuid = get_user_from(request)
    user = get_user(User, uuid)

    board_title = request.POST.get("board_title")

    if not board_title:
        return response_error("Board's name is required.")

    try:
        BoardValidations(board_title=board_title).result()
    except ModelsAttributeError as e:
        return response_error(f"Could not create the board: {e}")

    try:
        new_board = Board.objects.create(
            owner=user,
            name=board_title,
            creation_date=no_timezone(datetime.now()))
        new_board.save()
    except Exception as e:
        return response_error(f"Couldn't create the board: {e}")

    return redirect('core:board', board_id=new_board.id)


@HANDLER.bind("new_column", "board/<int:board_id>/new/column/", request="POST", session=True)
@requires_csrf_token
def new_column(request, board_id):
    """
    Creates a new column for the logged-in user.
    Requires the method to be POST and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board where the column will be added.
    :return: JsonResponse - The JSON response with the result of the operation.
    """
    uuid = get_user_from(request)

    if check_user_not_owner(Board, board_id, uuid):
        return response_error("You do not have access to this board.")

    board = get_board(Board, board_id)

    if check_board_invalid(board):
        return redirect('core:dashboard')

    title = request.POST.get("column_title")
    description = request.POST.get("column_description")
    color = request.POST.get("color")

    if not title or not description:
        return response_error("Title and description are required.")

    try:
        ColumnValidations(column_title=title, column_description=description, color=color).result()
    except ModelsAttributeError as e:
        return response_error(f"Could not create the column: {e}")

    column_index = get_columns(Column, board_id).count()

    if column_index != 0:
        column_index -= 1

    try:
        new_column = Column.objects.create(
            board_id=board,
            title=title,
            color=color,
            description=description,
            index=column_index
        )
        new_column.save()
    except Exception as e:
        return response_error(f"Couldn't create the column: {e}")

    return redirect('core:board', board_id=board_id)


@HANDLER.bind("new_card", "board/<int:board_id>/new/card/", request="POST", session=True)
@requires_csrf_token
def new_card(request, board_id):
    """
    Creates a new column for the logged-in user.
    :param request: HttpRequest - The HTTP request object.
    :param uuid: str - The UUID of the authenticated user passed by the RequestHandler.
    :return: JsonResponse - The JSON response with the result of the operation.
    """
    uuid = get_user_from(request)
    user = get_user_from(request)
    board = get_board(Board, board_id)

    if check_board_invalid(board):
        return redirect('core:dashboard')

    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You do not have access to this board.")

    title = request.POST.get("card_title")
    description = request.POST.get("card_description")
    color = request.POST.get("color")
    column_id = request.POST.get("column")
    date = request.POST.get("expiration_date", None)
    story_points = request.POST.get("story_points", 0)

    index = Card.objects.filter(column_id=column_id, board_id=board.id).count()

    if not title or not description:
        return response_error("Title and description are required.")

    if not column_id:
        return response_error("You must select a column to create a new card.")

    values = {
        "column_id":Column.objects.filter(id=column_id).first(),
        "board_id": board,
        "title":title,
        "description": description,
        "color": color,
        "creation_date": no_timezone(datetime.now()),
        "story_points": story_points,
        "index": index
    }
    if date:
        values["expiration_date"] = date

    try:
        CardValidations(**values).result()
    except ModelsAttributeError as e:
        return response_error(f"Could not create the card: {e}")

    try:
        new_card = Card.objects.create(**values)
        new_card.save()
    except Exception as e:
        return response_error(f"Couldn't create the card: {e}")

    return redirect('core:board', board_id=board_id)


@HANDLER.bind("board_update", "board/<int:board_id>/update/", request="POST", session=True)
@requires_csrf_token
def update_board(request, board_id):
    """
    Updates the board details.
    Requires the method to be POST and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board to update.
    :return: JsonResponse - The JSON response with the result of the operation.
    """
    uuid = get_user_from(request)
    user = get_user(User, uuid)
    board = get_board(Board, board_id)

    if check_board_invalid(board):
        return response_error("Board not found.")

    if check_user_not_owner(Board, board_id, uuid):
        return response_error("You are not the owner of this board.")

    updates = {
        'board_title': None,
        'board_description': None
    }

    for key in updates.keys():
        if not key in request.POST.keys():
            continue
        updates[key] = request.POST.get(key)

    updates = { k: v for k, v in updates.items() if v is not None }

    if img := request.FILES.get('image', None):
        updates['image'] = request.FILES.get('image')

    try:
        BoardValidations(**updates).result()
    except ModelsAttributeError as e:
        return response_error(f"Could not update this board's details: {e}")

    try:
        if img := updates.get('image', None):
            random_name = f"{uuid4()}{img.name[img.name.rfind('.'):]}"
            img.name = random_name
            board.image = img
        if title := updates.get('board_title', None):
            board.name = title
        if description := updates.get('board_description', None):
            board.description = description
        board.save()
    except Exception as e:
        return response_error(f"Couldn't update the board: {e}")

    return response_success("Board updated successfully.")


@HANDLER.bind("update_column", "board/<int:board_id>/column/<int:column_id>/update/", request="POST", session=True)
@requires_csrf_token
def update_column(request, board_id, column_id):
    """
    Updates the column details.
    Requires the method to be POST and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board to update.
    :param column_id: int - The ID of the column to update.
    :return: JsonResponse - The JSON response with the result of the operation.
    """
    uuid = get_user_from(request)
    user = get_user(User, uuid)
    board = get_board(Board, board_id)
    column = Column.objects.filter(id=column_id, board_id=board).first()

    if check_board_invalid(board):
        return response_error("Board not found.")

    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You are not the owner of this board.")

    if not column:
        return response_error("Column not found.")

    updates = {
        'column_title': None,
        'column_description': None,
        'column_color': None,
    }

    for key in updates.keys():
        if not key in request.POST.keys():
            continue
        updates[key] = request.POST.get(key)

    updates = { k: v for k, v in updates.items() if v is not None }

    try:
        ColumnValidations(**updates).result()
    except ModelsAttributeError as e:
        return response_error(f"Couldn't update this column: {e}")

    try:
        if title := updates.get('column_title', None):
            column.title = title
        if description := updates.get('column_description', None):
            column.description = description
        if color := updates.get('column_color', None):
            column.color = color
        column.save()
    except Exception as e:
        return response_error(f"Couldn't update the column: {e}")

    return response_success("Column updated successfully.")


@HANDLER.bind("board_update_elements", "board/<int:board_id>/update/elements/", session=True, request="POST")
def update_board_elements(request, board_id):
    uuid = get_user_from(request)
    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You do not have access to this board.")

    board = get_board(Board, board_id)
    columns = json.loads(request.body)

    for column in columns:
        column_id = int(column.get("id"))
        column_index = int(column.get("index"))
        col_instance = Column.objects.filter(id=column_id, board_id=board.id).first()
        col_instance.index = column_index
        col_instance.save()
        for card in column.get("cards"):
            card_id = int(card.get("id"))
            card_index = int(card.get("index"))
            card_instance = Card.objects.filter(id=card_id, board_id=board.id).first()
            card_instance.index = card_index
            card_instance.column_id = col_instance
            card_instance.save()

    return response_success("Board elements updated successfully.")


@HANDLER.bind("board_update_sync", "board/<int:board_id>/update/sync/", session=True, request="GET")
def sync_board(request, board_id):
    uuid = get_user_from(request)
    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You do not have access to this board.")

    board = get_board(Board, board_id)
    columns = get_board_elements(Column, Card, Assignee, User, board_id)
    return response_success(render(request, "modals/board_elements.html", {"columns": columns, "board": board}).content.decode("utf-8"))


@HANDLER.bind("update_card", "board/<int:board_id>/card/<int:card_id>/update/", request="POST", session=True)
@requires_csrf_token
def update_card(request, board_id, card_id):
    uuid = get_user_from(request)
    user = get_user(User, uuid)
    if not user:
        return response_error("User not found.")

    board = get_board(Board, board_id)
    if not board:
        return response_error("Board not found.")

    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You do not have access to this board.")

    card = Card.objects.filter(id=card_id, board_id=board).first()

    if not card:
        return response_error("Card not found.")

    updates = {
        'card_title': None,
        'card_description': None,
        'color': None,
        'expiration_date': None,
        'story_points': None,
        'completed': None
    }
    assignees = {}

    for key in request.POST.keys():
        if key in updates.keys():
            updates[key] = request.POST.get(key)
        elif key.startswith("assignee_"):
            assignees[key.removeprefix("assignee_")] = request.POST.get(key)

    updates = { k: v for k, v in updates.items() if v is not None }

    try:
        CardValidations(**updates).result()
    except ModelsAttributeError as e:
        return response_error(f"Could not update this card: {e}")

    try:
        if title := updates.get('card_title', None):
            card.title = title
        if description := updates.get('card_description', None):
            card.description = description
        if color := updates.get('color', None):
            card.color = color
        if date := updates.get('expiration_date', None):
            card.expiration_date = date
        if story_points := updates.get('story_points', None):
            card.story_points = story_points
        if completed := updates.get('completed', None):
            print(completed)
            if completed == "true":
                completed = no_timezone(datetime.now())
                card.completion_date = completed
            else:
                card.completion_date = None
        card.save()

        users = {get_user(User, username=assignee): False if value == "false" else True for assignee, value in assignees.items()}
        for assignee, value in users.items():
            if not assignee:
                print(assignee)
                continue
            params = {"card_id":card, "user_id":assignee, "board_id":board}
            exists = Assignee.objects.filter(**params).exists()
            if not exists and value:
                Assignee.objects.create(**params)
            elif exists and not value:
                Assignee.objects.filter(**params).delete()
            else:
                continue
    except Exception as e:
        return response_error(f"Couldn't update the card: {e}")

    return response_success("Card updated successfully.")

@HANDLER.bind("remove_board", "dashboard/remove/board/<int:board_id>/", request="POST", session=True)
@requires_csrf_token
def remove_board(request, board_id):

    uuid = get_user_from(request)
    user = get_user(User, uuid)
    board = get_board(Board, board_id)

    if not board:
        return response_error("Board not found.")

    if check_user_not_owner(Board, board_id, uuid):
        return response_error("You are not the owner of this board.")

    try:
        board.delete()
    except Exception as e:
        return response_error(f"Couldn't delete the board: {e}")

    return response_success("Board deleted successfully.")


@HANDLER.bind("remove_column", "board/<int:board_id>/remove/column/<int:column_id>/", request="POST", session=True)
@requires_csrf_token
def remove_column(request, board_id, column_id):

    uuid = get_user_from(request)
    user = get_user(User, uuid)
    board = get_board(Board, board_id)


    if not board:
        return response_error("Board not found.")

    if check_user_not_owner(Board, board_id, uuid):
        return response_error("You are not the owner of this board.")

    column = Column.objects.filter(id=column_id, board_id=board).first()

    if not column:
        return response_error("Column not found.")

    columns = Column.objects.filter(board_id=board, index__gt=column.index).all()
    columns.update(index=F('index') - 1)

    try:
        column.delete()
    except Exception as e:
        return response_error(f"Couldn't delete the board: {e}")

    return response_success("Column deleted successfully.")


@HANDLER.bind("remove_card", "board/<int:board_id>/remove/card/<int:card_id>/", request="POST", session=True)
@requires_csrf_token
def remove_card(request, board_id, card_id):
    uuid = get_user_from(request)
    user = get_user(User, uuid)
    board = get_board(Board, board_id)

    if not board:
        return response_error("Board not found.")

    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You are not the owner of this board.")

    card = Card.objects.filter(id=card_id, board_id=board).first()

    if not card:
        return response_error("Card not found.")

    cards = Card.objects.filter(column_id=card.column_id, index__gt=card.index).all()
    cards.update(index=F('index') - 1)

    try:
        card.delete()
    except Exception as e:
        return response_error(f"Couldn't delete the card: {e}")

    return response_success("Card deleted successfully.")


@HANDLER.bind("remove_user", "board/<int:board_id>/remove/user/", request="POST", session=True)
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

    if check_user_not_owner(Board, board_id, uuid):
        response_error("You don't own this board.")

    username_to_remove = request.POST.get("username")

    try:
        uuid = str(get_user(User, username=username_to_remove).uuid)
        if guest := get_guest(Guest, board_id, uuid):
            guest.delete()
    except Exception as e:
        return response_error(f"Error: {e}")

    return response_success(f"{username_to_remove} has been removed successfully from this board.")


@HANDLER.bind("new_board_modal", "dashboard/new/board/modal/", request="GET", session=True)
@requires_csrf_token
def new_board_modal(request):
    """
    Renders the modal for creating a new board.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :return: HttpResponse - The HTML response with the modal for creating a new board.
    """
    modal = render(request, "modals/new_board.html")
    return HttpResponse(modal)

@HANDLER.bind("new_column_modal", "board/<int:board_id>/new/column/modal/", request="GET", session=True)
@requires_csrf_token
def new_column_modal(request, board_id):
    """
    Renders the modal for creating a new column.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board where the column will be added.
    :return: HttpResponse - The HTML response with the modal for creating a new column.
    """
    uuid = get_user_from(request)
    if check_user_not_owner(Board, board_id, uuid):
        return response_error("You do not have access to this board.")

    modal = render(request, "modals/new_column.html", {'board_id': board_id})
    return HttpResponse(modal)


@HANDLER.bind("new_card_modal", "board/<int:board_id>/new/card/modal/", request="GET", session=True)
@requires_csrf_token
def new_card_modal(request, board_id):
    """
    Renders the modal for creating a new card.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board where the card will be added.
    :return: HttpResponse - The HTML response with the modal for creating a new card.
    """
    uuid = get_user_from(request)
    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You do not have access to this board.")

    columns = [{'id': column.id, 'title': column.title} for column in get_columns(Column, board_id)]
    if not columns:
        return response_error("No columns available. You must have at least one column before creating a card.")

    modal = render(request, "modals/new_card.html", {'columns': columns, 'board_id': board_id})
    return HttpResponse(modal)


@HANDLER.bind("update_column_modal", "board/<int:board_id>/column/<int:column_id>/modal/", request="GET", session=True)
@requires_csrf_token
def update_column_modal(request, board_id, column_id):
    """
    Renders the modal for updating a column.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board where the column will be updated.
    :param column_id: int - The ID of the column to update.
    """
    uuid = get_user_from(request)
    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You do not have access to this board.")

    board = get_board(Board, board_id)
    column = Column.objects.filter(id=column_id, board_id=board).first()
    arguments = {'board_id': board_id, 'column_id': column_id}

    modal = render(request, "modals/update_column.html", {
        'board_id': board_id,
        'column_id': column_id,
        'column': column
    })
    return HttpResponse(modal)


@HANDLER.bind("update_card_modal", "board/<int:board_id>/card/<int:card_id>/modal/", request="GET", session=True)
@requires_csrf_token
def update_card_modal(request, board_id, card_id):
    """
    Renders the modal for updating a card.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board where the card will be added.
    :return: HttpResponse - The HTML response with the modal for creating a new card
    """
    uuid = get_user_from(request)

    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You do not have access to this board.")

    board = get_board(Board, board_id)
    card = Card.objects.filter(id=card_id, board_id=board).first()

    if not card:
        return response_error("Card not found.")

    class TemplateUser:
        def __init__(self, user):
            nonlocal card
            self.username = user.username
            self.is_assigned = Assignee.objects.filter(card_id=card, user_id=user).exists()

    guests = [guest.user_id.uuid for guest in Guest.objects.filter(board_id=board)] + [board.owner.uuid]
    users = User.objects.filter(uuid__in=guests)

    users = [TemplateUser(user) for user in users]

    modal = render(request, "modals/update_card.html", {
        'board_id': board_id,
        'card_id': card_id,
        'card': card,
        'users': users
    })
    return HttpResponse(modal)


@HANDLER.bind("remove_board_modal", "dashboard/remove/board/<int:board_id>/modal/", request="GET", session=True)
@requires_csrf_token
def remove_board_modal(request, board_id):
    """
    Renders the modal for removing a board.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board to remove.
    :return: HttpResponse - The HTML response with the modal for removing a board
    """
    uuid = get_user_from(request)

    if check_user_not_owner(Board, board_id, uuid):
        return response_error("You are not allowed to invite someone to this board. You are not the Owner!")

    name = get_board(Board, board_id).name
    arguments = {'board_id': board_id}

    modal = render(request, "modals/remove_something.html", {
        "view": reverse('core:remove_board', kwargs=arguments),
        "title": name,
        "type": "Board"
    })
    return HttpResponse(modal)


@HANDLER.bind("remove_column_modal", "board/<int:board_id>/remove/column/<int:column_id>/modal/", request="GET", session=True)
@requires_csrf_token
def remove_column_modal(request, board_id, column_id):
    """
    Renders the modal for removing a column.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board where the column will be removed.
    :param column_id: int - The ID of the column to remove.
    :return: HttpResponse - The HTML response with the modal for removing a column.
    """
    uuid = get_user_from(request)

    if check_user_not_owner(Board, board_id, uuid):
        return response_error("You are not allowed to invite someone to this board. You are not the Owner!")

    board = get_board(Board, board_id)
    title = Column.objects.filter(id=column_id, board_id=board).first().title
    arguments = {'board_id': board_id, 'column_id': column_id}

    modal = render(request, "modals/remove_something.html", {
        "view": reverse('core:remove_column', kwargs=arguments),
        "title": title,
        "type": "Column"
    })
    return HttpResponse(modal)


@HANDLER.bind("remove_card_modal", "board/<int:board_id>/remove/card/<int:card_id>/modal/", request="GET", session=True)
@requires_csrf_token
def remove_card_modal(request, board_id, card_id):
    """
    Renders the modal for removing a card.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board where the card will be removed.
    :param card_id: int - The ID of the card to remove.
    :return: HttpResponse - The HTML response with the modal for removing a card.
    """
    uuid = get_user_from(request)

    if check_user_not_owner_or_guest(Board, Guest, board_id, uuid):
        return response_error("You do not have access to this board.")

    board = get_board(Board, board_id)
    card = Card.objects.filter(id=card_id, board_id=board).first()
    column_title = Column.objects.filter(id=card.column_id.id).first().title

    arguments = {'board_id': board_id, 'card_id': card_id}

    modal = render(request, "modals/remove_something.html", {
        "view": reverse('core:remove_card', kwargs=arguments),
        "title": f"{column_title} - {card.title}",
        "type": "Card"
    })
    return HttpResponse(modal)


@HANDLER.bind("manage_assignees", "board/<int:board_id>/new/user/", request="POST", session=True)
@requires_csrf_token
def invite_user(request, board_id):
    uuid = get_user_from(request)
    board = get_board(Board, board_id)

    if not board:
        return response_error("Board not found.")

    if check_user_not_owner(Board, board_id, uuid):
        return response_error("You are not allowed to invite someone to this board. You are not the Owner!")

    guests = []
    for key in request.POST.keys():
        if key.startswith("user_"):
            guests.append(request.POST.get(key))

    guests = [get_user(User, username=username) for username in guests]

    Guest.objects.filter(board_id=board).exclude(user_id__in=guests).delete()

    for guest in guests:
        if not Guest.objects.filter(board_id=board, user_id=guest).exists():
            Guest.objects.create(board_id=board, user_id=guest)

    return response_success("Changes committed successfully.")



@HANDLER.bind("new_user_modal", "board/<int:board_id>/new/user/modal/", request="GET", session=True)
@requires_csrf_token
def invite_user_modal(request, board_id):
    """
    Renders the modal for inviting a new user to the board.
    Requires the method to be GET and the user to be authenticated.

    :param request: HttpRequest - The HTTP request object.
    :param board_id: int - The ID of the board where the user will be invited.
    :return: HttpResponse - The HTML response with the modal for inviting a new user.
    """
    uuid = get_user_from(request)

    if check_user_not_owner(Board, board_id, uuid):
        return response_error("You are not allowed to invite someone to this board. You are not the Owner!")

    users = User.objects.all().exclude(uuid=uuid) # Remove the owner of the board from the list of users to invite
    assignees = [user for user in users if not check_user_not_guest(Guest, board_id, user.uuid)] # Find all guests of the board
    users = users.exclude(uuid__in=[assignee.uuid for assignee in assignees]) # Find all users not in the already assigned list

    modal = render(request, "modals/manage_users.html", {
        'board_id': board_id,
        'users': users,
        'assignees': assignees
    })
    return HttpResponse(modal)


@HANDLER.bind("acceptance_deletion", "acceptance/delete/", request="GET", session=False)
@requires_csrf_token
def acceptance_deletion(request):

    User.objects.filter(username="acceptancetest").delete()
    # Board.objects.filter(name="Acceptance Board").delete()

    request.session.flush()
    print("Deleted acceptance user.")

    return redirect(reverse('no_auth:login'))

