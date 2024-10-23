from datetime import datetime

from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone

from authentication.models import User
from core.models import Board, Card, Guest
from static.services import JsonResponses

response = lambda status, message: JsonResponses.response(status, message)
response_error = lambda message: JsonResponses.response(JsonResponses.ERROR, message)
response_warn = lambda message: JsonResponses.response(JsonResponses.WARNING, message)
response_success = lambda message: JsonResponses.response(JsonResponses.SUCCESS, message)


def get_user_from(request: HttpRequest) -> str:
    """
    Gets the user from the request session.

    :param request: The request object.
    :returns: The user's UUID.
    """
    return request.session.get('uuid', None)


def check_user_invalid(uuid: str) -> bool:
    """
    Checks if the user is invalid.

    :param uuid: The user's UUID to check.
    :returns: The sum of the two input integers.
    """
    return uuid is None


def check_board_invalid(board: Board) -> bool:
    """
    Checks if the board is invalid (None).

    :param board: The board object.
    :return: True if the board is invalid, False otherwise.
    """
    return board is None


def get_board(board, board_id: int, owner: str = None) -> Board or None:
    """
    Gets the Board by the board_id from the model.

    :param board: The board model.
    :param board_id: The board's ID.
    :param owner: The board's owner.
    :return: The board object, None otherwise.
    """
    keywords = { 'id': board_id }

    if owner:
        keywords['owner'] = owner

    return board.objects.filter(**keywords).first()


def get_cards_of_board(card, board_id: int) -> QuerySet[Card]:
    """
    Gets the cards of the board.

    :param card: The card model.
    :param board_id: The board's ID.
    :return: The cards of the board.
    """
    return card.objects.filter(board_id=board_id)


def get_expired_cards_of_board(card, board_id: int) -> QuerySet[Card]:
    """
    Gets the expired cards of the board.

    :param card: The card model.
    :param board_id: The board's ID.
    :return: The expired cards of the board.
    """
    return get_cards_of_board(card, board_id).filter(expiration_date__lt=timezone.now())


def get_user(user, uuid: str = None, username: str = None) -> User or None:
    """
    Gets the User by the user_id OR by the username from the model.

    :param user: The user model.
    :param uuid: The user's UUID.
    :param username: The user's username.
    :return: The user object.
    """
    keywords = {}

    if uuid:
        keywords = { 'uuid': uuid }

    if username:
        keywords = { 'username': username }

    return user.objects.filter(**keywords).first()


def get_guest(guest, board_id: int, uuid: str) -> Guest or None:
    """
    Gets the Guest by the user and board_id from the model.

    :param guest: The guest model.
    :param uuid: The user's UUID.
    :param board_id: The board's ID.
    :return: The guest object, None otherwise.
    """
    return guest.objects.filter(user_id=uuid, board_id=board_id).first()


def check_user_not_owner(board, board_id: int, uuid: str) -> bool:
    """
    Checks if the user is not the owner of the board.

    :param board: The board model.
    :param board_id: The board's ID.
    :param uuid: The user's UUID.
    :return: True if the user is not the owner, False otherwise.
    """
    return get_board(board, board_id, uuid) is None


def check_user_not_guest(guest, board_id: int, uuid: str) -> bool:
    """
    Checks if the user is not a guest of the board.

    :param guest: The guest model.
    :param uuid: The user's UUID.
    :param board_id: The board's ID.
    :return: True if the user is not a guest, False otherwise.
    """
    return get_guest(guest, board_id, uuid) is None


def check_user_not_owner_or_guest(board, guest, uuid: str, board_id: int) -> bool:
    """
    Checks if the user is not the owner or a guest of the board.

    :param board: The board model.
    :param guest: The guest model.
    :param uuid: The user's UUID.
    :param board_id: The board's ID.
    :return: True if the user is not the owner or a guest, False otherwise.
    """
    return check_user_not_owner(board, board_id, uuid) and check_user_not_guest(guest, board_id, uuid)


def no_timezone(dt: datetime) -> datetime:
    """
    Removes the timezone from the datetime object.

    :param dt: The datetime object.
    :return: The datetime object without timezone.
    """
    return dt.replace(tzinfo=None)

