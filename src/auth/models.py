from django.db import models

from Kanboard.settings import BASE_DIR
from static.services import register

# Create your models here.
database = BASE_DIR / 'db.sqlite3'
app_name = "auth"


@register(database, app_name)
class User(models.Model):
    uuid = models.UUIDField(primary_key=True)
    username = models.CharField(max_length=16, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=32)
    image = models.ImageField()
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)

    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()

    def __str__(self):
        return self.name
