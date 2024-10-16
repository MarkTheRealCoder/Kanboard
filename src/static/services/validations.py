import re

from django.db.migrations.serializer import UUIDSerializer


class ModelsAttributeError(Exception):
    class Reason(int):
        pass

    PATTERN = Reason(1)
    EXISTENCE = Reason(2)

    def __init__(self, msg: str = "", reason: Reason = PATTERN):
        self.___reason: 'Reason' = reason
        super().__init__(msg)

    def is_pattern(self) -> bool:
        return self.___reason == self.PATTERN

    def is_existence(self) -> bool:
        return self.___reason == self.EXISTENCE

    def __str__(self):
        return super().__str__()


PATTERN = ModelsAttributeError.PATTERN
EXISTENCE = ModelsAttributeError.EXISTENCE


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

    def result(self) -> 'UserValidations':
        self.___validate_name()
        self.___validate_surname()
        self.___validate_username()
        self.___validate_email()
        self.___validate_password()
        self.___validate_image()
        return self

    def ___validate_username(self):
        if self.username is None:
            return
        if re.match(r'^[a-zA-Z0-9_]+$', self.username) is None:
            raise ModelsAttributeError("Username must contain only letters, numbers and underscores")
        if self.klass.objects.filter(username=self.username).exists():
            raise ModelsAttributeError("Username already exists", EXISTENCE)

    def ___validate_email(self):
        if self.email is None:
            return
        if re.match(r'^[a-zA-Z0-9_]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]+$', self.email) is None:
            raise ModelsAttributeError("Email must be in the format: youremail@example.com")
        if self.klass.objects.filter(email=self.email).exists():
            raise ModelsAttributeError("Email already exists", EXISTENCE)

    def ___validate_password(self):
        if self.password is None:
            return
        if re.match(r'^[a-zA-Z0-9\_\%\$\&\,\@\!\?]{8,}$', self.password) is None:
            raise ModelsAttributeError("Password must contain only letters, numbers and/or special characters: '_', '!', '@', '$', '%', '&', '?', ','.\n"
                                       "Password must be at least 8 characters long")

    def ___validate_image(self):
        if self.image is None:
            return
        if not re.match(r'^image\/(jpeg|png|jpg)$', self.image.content_type):
            raise ModelsAttributeError("Image must be in the format: jpeg, png or jpg")
        if self.image.size > 3*1024*1024:
            raise ModelsAttributeError("Image size must be less than 3MB")

    def ___validate_name(self):
        if self.name is None:
            return
        if re.match(r'^[a-zA-Z]+$', self.name) is None:
            raise ModelsAttributeError("Name must contain only letters")

    def ___validate_surname(self):
        if self.surname is None:
            return
        if re.match(r'^[a-zA-Z]+$', self.surname) is None:
            raise ModelsAttributeError("Surname must contain only letters")

class BoardValidations:
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', None)
        self.description = kwargs.get('description', None)
        self.image = kwargs.get('image', None)

    def result(self):
        self.___validate_title()
        self.___validate_description()
        self.___validate_image()

    def ___validate_title(self):
        if self.title is None:
            return
        if not re.match(r'^[a-zA-Z0-9 ]{1,16}$', self.title):
            raise ModelsAttributeError(
                "Title must be 16 characters or less and must contain only letters, numbers, and the special character: '_'.")

    def ___validate_description(self):
        if self.description is None:
            return
        if re.match(r'^[a-zA-Z0-9 .,;:!?-_()\n]{1,256}$', self.description) is None:
            raise ModelsAttributeError(
                "Description contains invalid characters or exceeds 256 characters. Accepted characters are "
                "letters, numbers, spaces, newlines, and the following special characters: '.', ',', ';', ':', '!', '?', '-', '', '(', ')'.")

    def ___validate_image(self):
        if self.image is None:
            return
        if self.image.size > 3 * 1024 * 1024:
            raise ModelsAttributeError("Image size must be less than 3MB.")
        if not re.match(r'^image/(jpeg|png|jpg)$', self.image.content_type):
            raise ModelsAttributeError("Image must be in the format: jpeg, png or jpg.")


class ColumnValidations:
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', None)
        self.description = kwargs.get('description', None)
        self.color = kwargs.get('color', None)
        self.image = kwargs.get('image', None)

    def result(self):
        self.___validate_title()
        self.___validate_description()
        self.___validate_color()
        self.___validate_image()

    def ___validate_title(self):
        if self.title is None:
            return
        if not re.match(r'^[a-zA-Z0-9 ]{1,20}$', self.title):
            raise ModelsAttributeError(
                "Title must be 20 characters or less and must contain only letters, numbers, and the special character: ''.")

    def ___validate_description(self):
        if self.description is None:
            return
        if re.match(r'^[a-zA-Z0-9 .,;:!?-_()\n]{1,256}$', self.description) is None:
            raise ModelsAttributeError(
                "Description contains invalid characters or exceeds 256 characters. Accepted characters are "
                "letters, numbers, spaces, newlines, and the following special characters: '.', ',', ';', ':', '!', '?', '-', '', '(', ')'.")

    def ___validate_color(self):
        if self.color is None:
            return
        if not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            raise ModelsAttributeError("Color must be in the format #RRGGBB (hexadecimal).")

    def ___validate_image(self):
        if self.image is None:
            return
        if self.image.size > 3 * 1024 * 1024:
            raise ModelsAttributeError("Image size must be less than 3MB.")
        if not re.match(r'^image/(jpeg|png|jpg)$', self.image.content_type):
            raise ModelsAttributeError("Image must be in the format: jpeg, png or jpg.")


class CardValidations:
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', None)
        self.description = kwargs.get('description', None)
        self.color = kwargs.get('color', None)
        self.image = kwargs.get('image', None)

    def result(self):
        self.___validate_title()
        self.___validate_description()
        self.___validate_color()
        self.___validate_image()

    def ___validate_title(self):
        if self.title is None:
            return
        if not re.match(r'^[a-zA-Z0-9 ]{1,20}$', self.title):
            raise ModelsAttributeError(
                "Title must be 20 characters or less and must contain only letters, numbers, and the special character: ''.")

    def ___validate_description(self):
        if self.description is None:
            return
        if re.match(r'^[a-zA-Z0-9 .,;:!?-_()\n]{1,256}$', self.description) is None:
            raise ModelsAttributeError(
                "Description contains invalid characters or exceeds 256 characters. Accepted characters are "
                "letters, numbers, spaces, newlines, and the following special characters: '.', ',', ';', ':', '!', '?', '-', '', '(', ')'.")

    def ___validate_color(self):
        if self.color is None:
            return
        if not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            raise ModelsAttributeError("Color must be in the format #RRGGBB (hexadecimal).")

    def ___validate_image(self):
        if self.image is None:
            return
        if self.image.size > 3 * 1024 * 1024:
            raise ModelsAttributeError("Image size must be less than 3MB.")
        if not re.match(r'^image/(jpeg|png|jpg)$', self.image.content_type):
            raise ModelsAttributeError("Image must be in the format: jpeg, png or jpg.")

