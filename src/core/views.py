from django.shortcuts import render

from Kanboard.settings import BASE_DIR
from core.models import Board
from static.services import RequestHandler, DBRequestBuilder, DBHybridTable, DBHybridField
from django.contrib import messages

# Create your views here.

app_name = "core"
