from django.contrib import admin

from core.models import Board, Column, Guest, Card, Assignee

# Register your models here.
admin.site.register(Board)
admin.site.register(Column)
admin.site.register(Card)
admin.site.register(Guest)
admin.site.register(Assignee)