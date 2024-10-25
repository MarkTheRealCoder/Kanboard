from django.db import models


# Create your models here.
APP_NAME = "authentication"


class User(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False)
    username = models.CharField(max_length=16, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=32)
    image = models.ImageField(null=True, blank=True)
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()

    def __str__(self):
        return self.name
