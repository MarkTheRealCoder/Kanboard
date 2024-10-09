import re

from django.db.migrations.serializer import UUIDSerializer


class ModelsAttributeError(Exception):
    pass


class UserValidations:
    def __init__(self, klass, **kwargs):
        self.klass = klass
        self.username = kwargs.get('username', None)
        self.email = kwargs.get('email', None)
        self.password = kwargs.get('password', None)
        self.image = kwargs.get('image', None)
        self.name = kwargs.get('name', None)
        self.surname = kwargs.get('surname', None)

    def generate_uuid(self):
        import uuid
        return uuid.uuid1()

    def result(self):
        self.___validate_username()
        self.___validate_email()
        self.___validate_password()
        self.___validate_image()
        self.___validate_name()
        self.___validate_surname()

    def ___validate_username(self):
        if self.klass.objects.filter(username=self.username).exists():
            raise ModelsAttributeError("Username already exists.")
        if re.match(r'^[a-zA-Z0-9_]+$', self.username) is None:
            raise ModelsAttributeError("Username must contain only letters, numbers and underscores.")

    def ___validate_email(self):
        if self.klass.objects.filter(email=self.email).exists():
            raise ModelsAttributeError("Email already exists.")
        if re.match(r'^[a-zA-Z0-9_]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]+$', self.email) is None:
            raise ModelsAttributeError("Email must be in the format: youremail@example.com")

    def ___validate_password(self):
        if re.match(r'^[a-zA-Z0-9\_\%\$\&\,\@\!\?]{8,}$', self.password) is None:
            raise ModelsAttributeError("Password must contain only letters, numbers and/or special characters: '_', '!', '@', '$', '%', '&', '?', ','.\n"
                                 "Password must be at least 8 characters long.")

    def ___validate_image(self):
        if self.image.size > 3*1024*1024:
            raise ModelsAttributeError("Image size must be less than 3MB.")
        if not re.match(r'^image\/(jpeg|png|jpg)$', self.image.content_type):
            raise ModelsAttributeError("Image must be in the format: jpeg, png or jpg.")

    def ___validate_name(self):
        if re.match(r'^[a-zA-Z]+$', self.name) is None:
            raise ModelsAttributeError("Name must contain only letters.")

    def ___validate_surname(self):
        if re.match(r'^[a-zA-Z]+$', self.surname) is None:
            raise ModelsAttributeError("Surname must contain only letters.")


