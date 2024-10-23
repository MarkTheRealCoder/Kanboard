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
    return request.session.get('uuid', None)


def check_user_invalid(uuid: str) -> bool:
    return uuid is None


def check_board_invalid(board: Board) -> bool:
    return board is None


def get_board(board, board_id: int, owner: str = None) -> Board or None:
    keywords = { 'id': board_id }

    if owner:
        keywords['owner'] = owner

    return board.objects.filter(**keywords).first()


def get_cards_of_board(card, board_id: int) -> QuerySet[Card]:
    return card.objects.filter(board_id=board_id)


def get_expired_cards_of_board(card, board_id: int) -> QuerySet[Card]:
    return get_cards_of_board(card, board_id).filter(expiration_date__lt=timezone.now())


def get_user(user, uuid: str = None, username: str = None) -> User or None:
    keywords = {}

    if uuid:
        keywords = { 'uuid': uuid }

    if username:
        keywords = { 'username': username }

    return user.objects.filter(**keywords).first()


def get_guest(guest, board_id: int, uuid: str) -> Guest or None:
    return guest.objects.filter(user_id=uuid, board_id=board_id).first()


def check_user_not_owner(board, board_id: int, uuid: str) -> bool:
    return get_board(board, board_id, uuid) is None


def check_user_not_guest(guest, board_id: int, uuid: str) -> bool:
    return get_guest(guest, board_id, uuid) is None


def check_user_not_owner_or_guest(board, guest, uuid: str, board_id: int) -> bool:
    return check_user_not_owner(board, board_id, uuid) and check_user_not_guest(guest, board_id, uuid)


def no_timezone(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None)