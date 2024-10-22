from django.db import models

from Kanboard.settings import BASE_DIR
from authentication.models import User


# Create your models here.
APP_NAME = "core"


class Board(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, db_column="owner")
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(blank=True, null=True)
    creation_date = models.DateTimeField()

    def __str__(self):
        return self.name


class Guest(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE, db_column="board_id")

    class Meta:
        unique_together = ('user_id', 'board_id')

    def __str__(self):
        return f"{self.user_id} - {self.board_id}"


class Column(models.Model):
    id = models.AutoField(primary_key=True)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE, db_column="board_id")
    title = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#808080")
    description = models.TextField()
    index = models.IntegerField()

    class Meta:
        unique_together = ('id', 'board_id')

    def __str__(self):
        return self.title


class Card(models.Model):
    id = models.AutoField(primary_key=True)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE, db_column="board_id")
    column_id = models.ForeignKey(Column, on_delete=models.CASCADE, db_column="column_id")
    title = models.CharField(max_length=100)
    description = models.TextField()
    color = models.CharField(max_length=7, default="#808080")
    creation_date = models.DateTimeField()
    expiration_date = models.DateTimeField(null=True, blank=True, default=None)
    completion_date = models.DateTimeField(null=True, blank=True, default=None)
    story_points = models.IntegerField(default=0)
    index = models.IntegerField()

    class Meta:
        unique_together = ('id', 'board_id')

    def __str__(self):
        return self.title


# class JoinRequest(models.Model):
#     id = models.AutoField(primary_key=True)
#     user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
#     board_id = models.ForeignKey(Board, on_delete=models.CASCADE, db_column="board_id")
#     status = models.BooleanField(null=True, default=None)
#
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['user_id', 'board_id'],
#                 condition=models.Q(status__isnull=True),
#                 name='unique_id1_id2_when_null'
#             ),
#         ]
#
#     def __str__(self):
#         return f"{self.user_id} - {self.board_id}"

