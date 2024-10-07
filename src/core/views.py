from django.shortcuts import render

from Kanboard.settings import BASE_DIR
from core.models import Board
from static.services import RequestHandler, DBRequestBuilder, DBHybridTable, DBHybridField
from django.contrib import messages

# Create your views here.

app_name = "core"

HANDLER = RequestHandler(f"{BASE_DIR}/db.sqlite3")

data = (
    DBRequestBuilder("core", "column_details", "No column found with this ID!")
    .select("id", "title", "description", "color", "index")
    .from_table("columns")
    .where("id = PARAM(column_id)"),

)


@HANDLER.bind("column_details", "<int:column_id>/columndetails", *data)
    """
    Executes the query to retrieve column details.

    :param request: HttpRequest - The HTTP request object.
    :param column_details: str - The result of the column details query.
    :return: HttpResponse - The rendered HTML page with column details.
    """
def column_details_view(request, column_details):
    return render(request, "column_details.html", {
        "column": column_details
    })



data = (
    DBRequestBuilder("core", "card_details", "No card found with this ID!")
    .select("id", "title", "description", "color", "creation_date", "expiration_date", "story_points")
    .from_table("cards")
    .where("id = PARAM(card_id)"),

)


@HANDLER.bind("card_details", "<int:card_id>/carddetails", *data)
def card_detail_view(request, card_details):
    """
    Executes the query to retrieve card details.

    :param request: HttpRequest - The HTTP request object.
    :param card_details: str - The result of the card details query.
    :return: HttpResponse - The rendered HTML page with card details.
    """
    
    return render(request, "card_details.html", {
        "card": card_details
    })


data = (
    DBRequestBuilder("auth", "user_details", "No user found with this ID!")
    .select("uuid", "username", "email", "name", "surname", "last_login", "date_joined")
    .from_table("user")
    .where("uuid = PARAM(user_id)"),

)


@HANDLER.bind("user_details", "<int:user_id>/userdetails", *data)
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



data = (
    DBRequestBuilder("core", "board_details", "No board found with this ID!")
    .select("id", "name", "description", "image", "creation_date")
    .from_table("boards")
    .where("id = PARAM(board_id)"),
)


@HANDLER.bind("board_details", "<int:board_id>/details", *data)
def board_details_view(request, board_details):
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
    DBRequestBuilder("core", "column_cards", "No cards found for this column!")
    .select("id", "title", "description", "color", "creation_date", "expiration_date", "story_points", "index")
    .from_table("cards")
    .where("column_id = PARAM(column_id)"),
)


@HANDLER.bind("column_cards", "<int:column_id>/cards", *data)
def column_cards_view(request, column_cards):
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
    DBRequestBuilder("core", "expired_cards", "No expired cards found for this user!")
    .select("id", "title", "description", "expiration_date")
    .from_table("cards")
    .where("expiration_date < NOW() AND owner_id = PARAM(user_id)"),
)


@HANDLER.bind("expired_cards", "<int:user_id>/expired", *data)
def expired_cards_view(request, expired_cards):
    """
    Executes the query to retrieve the list of expired cards for a user.

    :param request: HttpRequest - The HTTP request object.
    :param expired_cards: str - The result of the expired cards query.
    :return: HttpResponse - The rendered HTML page with the list of expired cards.
    """
    return render(request, "expired_cards.html", {
        "cards": list(expired_cards)
    })

