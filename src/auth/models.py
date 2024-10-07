from django.db import models

from Kanboard.settings import BASE_DIR
from static.services import register

# Create your models here.
database = BASE_DIR / 'db.sqlite3'
app_name = "auth"


@register(database, app_name)
class User(models.Model):
    uuid = models.UUIDField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    image = models.ImageField(width_field=100, height_field=100)

    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()

    def __str__(self):
        return self.name