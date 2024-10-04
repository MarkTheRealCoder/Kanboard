from django.db import models

from auth.models import User


# Create your models here.

class Board(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(width_field=100, height_field=100)
    creation_date = models.DateTimeField()

    def __str__(self):
        return self.name


class Guests(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"{self.user_id} - {self.board_id}"


class Column(models.Model):
    id = models.AutoField(primary_key=True)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE, primary_key=True)
    title = models.CharField(max_length=100)
    color = models.CharField(max_length=7)
    description = models.TextField()
    index = models.IntegerField()

    def __str__(self):
        return self.title


class Card(models.Model):
    id = models.AutoField(primary_key=True)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE, primary_key=True)
    column_id = models.ForeignKey(Column, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    color = models.CharField(max_length=7)
    creation_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    story_points = models.IntegerField()
    index = models.IntegerField()

    def __str__(self):
        return self.title

