from typing import Literal

from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone

from core.models import Board, Card, Guest
from static.services import JsonResponses


response = lambda status, message: JsonResponses.response(status, message)
response_error = lambda message: JsonResponses.response(JsonResponses.ERROR, message)
response_warn = lambda message: JsonResponses.response(JsonResponses.WARNING, message)
response_success = lambda message: JsonResponses.response(JsonResponses.SUCCESS, message)


def get_user_from(request: HttpRequest) -> str:
    return request.session.get('uuid', None)


def check_user_invalid(user: str) -> bool:
    return user is None


def get_board(board, board_id: int) -> Board:
    return board.objects.filter(id=board_id).first()


def check_board_invalid(board: Board) -> bool:
    return board is None


def check_user_not_owner(board, user: str) -> bool:
    return not board.objects.filter(owner_id=user).exists()


def check_user_not_guest(guests, user: str, board_id: int) -> bool:
    return not guests.objects.filter(user_id=user, board_id=board_id).exists()


def check_user_not_owner_or_guest(board, guests, user: str, board_id: int) -> bool:
    return check_user_not_owner(board, user) and check_user_not_guest(guests, user, board_id)


def get_cards_of_board(card, board_id: int) -> QuerySet[Card]:
    return card.objects.filter(board_id=board_id)


def get_expired_cards_of_board(card, board_id: int) -> QuerySet[Card]:
    return card.objects.filter(board_id=board_id, expiration_date__lt=timezone.now())

# Minchia ma che è sto file? il muro del pianto?
# Per rimanere in tema: La muraglia cinese