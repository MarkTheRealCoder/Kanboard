from django.db import models

from Kanboard.settings import BASE_DIR
from auth.models import User
from static.services import register


# Create your models here.

database = BASE_DIR / 'db.sqlite3'
app_name = "core"


@register(database, app_name)
class Board(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(width_field=100, height_field=100)
    creation_date = models.DateTimeField()


    def __str__(self):
        return self.name


@register(database, app_name)
class Guests(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user_id', 'board_id')

    def __str__(self):
        return f"{self.user_id} - {self.board_id}"


@register(database, app_name)
class Column(models.Model):
    id = models.AutoField(primary_key=True)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    color = models.CharField(max_length=7)
    description = models.TextField()
    index = models.IntegerField()

    class Meta:
        unique_together = ('id', 'board_id')

    def __str__(self):
        return self.title


@register(database, app_name)
class Card(models.Model):
    id = models.AutoField(primary_key=True)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)
    column_id = models.ForeignKey(Column, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    color = models.CharField(max_length=7)
    creation_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    story_points = models.IntegerField()
    index = models.IntegerField()

    class Meta:
        unique_together = ('id', 'board_id')

    def __str__(self):
        return self.title

