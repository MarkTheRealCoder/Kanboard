import re


class ModelsAttributeError(Exception):
    """
    Custom exception class for model attribute errors.
    The exception is raised when a model attribute is invalid.

    The exception is raised with a message and a reason.
    The reason is a shadow-type integer that represents the type of error.
    """
    class Reason(int):
        pass

    PATTERN = Reason(1)
    EXISTENCE = Reason(2)

    def __init__(self, msg: str = "", reason: Reason = PATTERN):
        if not isinstance(reason, self.Reason):
            raise ValueError("Invalid reason type")
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
    def __init__(self, klass = None, **kwargs):
        self.___klass = klass
        self.___username = kwargs.get('username', None)
        self.___email = kwargs.get('email', None)
        self.___password = kwargs.get('password', None)
        self.___image = kwargs.get('image', None)
        self.___name = kwargs.get('name', None)
        self.___surname = kwargs.get('surname', None)

    def generate_uuid(self) -> str:
        """
        Generate a unique identifier for the user.

        :return: the unique identifier.
        """
        import uuid
        return uuid.uuid4().hex

    def result(self) -> 'UserValidations':
        self.___validate_name()
        self.___validate_surname()
        self.___validate_username()
        self.___validate_email()
        self.___validate_password()
        self.___validate_image()
        return self

    def ___validate_username(self):
        if self.___username is None:
            return
        if re.match(r'^[a-zA-Z0-9_]{1,32}$', self.___username) is None:
            raise ModelsAttributeError("Username must contain only letters, numbers and underscores.\n"
                                       "Username must not exceed 32 characters.")
        if self.___klass and self.___klass.objects.filter(username=self.___username).exists():
            raise ModelsAttributeError("Username already exists", EXISTENCE)

    def ___validate_email(self):
        if self.___email is None:
            return
        if re.match(r'^[a-zA-Z0-9_.]+@[a-zA-Z0-9.]+\.[a-zA-Z0-9]+$', self.___email) is None:
            raise ModelsAttributeError("Email must be in the format: youremail@example.com")
        if self.___klass and self.___klass.objects.filter(email=self.___email).exists():
            raise ModelsAttributeError("Email already exists", EXISTENCE)

    def ___validate_password(self):
        if self.___password is None:
            return
        if re.match(r'^[a-zA-Z0-9_%$&@!?]{8,32}$', self.___password) is None:
            raise ModelsAttributeError("Password must contain only letters, numbers and/or special characters: '_', '!', '@', '$', '%', '&', '?'.\n"
                                       "Password must be at least 8 characters long and must not exceed 32 characters.")

    def ___validate_image(self):
        if self.___image is None:
            return
        if not re.match(r'^image/(jpeg|png|jpg)$', self.___image.content_type):
            raise ModelsAttributeError("Image must be in the format: jpeg, png or jpg")
        if self.___image.size > 3*1024*1024:
            raise ModelsAttributeError("Image size must be less than 3MB")

    def ___validate_name(self):
        if self.___name is None:
            return
        if re.match(r'^[a-zA-Z]{1,32}$', self.___name) is None:
            raise ModelsAttributeError("Name must contain only letters.\n"
                                       "Name must not exceed 32 characters.")

    def ___validate_surname(self):
        if self.___surname is None:
            return
        if re.match(r'^[a-zA-Z ]{1,32}$', self.___surname) is None:
            raise ModelsAttributeError("Surname must contain only letters.\n"
                                       "Surname must not exceed 32 characters.")


class BoardValidations:
    def __init__(self, **kwargs):
        self.___title = kwargs.get('board_title', None)
        self.___description = kwargs.get('board_description', None)
        self.___image = kwargs.get('image', None)

    def result(self):
        self.___validate_title()
        self.___validate_description()
        self.___validate_image()

    def ___validate_title(self):
        if self.___title is None:
            return
        if not re.match(r'^[a-zA-Z0-9 ]{1,20}$', self.___title):
            raise ModelsAttributeError(
                "Title must be 16 characters or less and must contain only letters, numbers, and the special "
                "character: '_'.")

    def ___validate_description(self):
        if self.___description is None:
            return
        if re.match(r"""^[a-zA-Z0-9 '".,;:!?-_()\n]{0,256}$""", self.___description) is None:
            raise ModelsAttributeError(
                "Description contains invalid characters or exceeds 256 characters. Accepted characters are "
                "letters, numbers, spaces, newlines, and the following special characters: '.', ',', ';', ':', '!', "
                "'?', '-', '', '(', ')'.")

    def ___validate_image(self):
        if self.___image is None:
            return
        if self.___image.size > 3 * 1024 * 1024:
            raise ModelsAttributeError("Image size must be less than 3MB.")
        if not re.match(r'^image/(jpeg|png|jpg)$', self.___image.content_type):
            raise ModelsAttributeError("Image must be in the format: jpeg, png or jpg.")


class ColumnValidations:
    def __init__(self, **kwargs):
        self.___title = kwargs.get('column_title', None) or kwargs.get('title', None)
        self.___description = kwargs.get('column_description', None) or kwargs.get('description', None)
        self.___color = kwargs.get('color', None)

    def result(self):
        self.___validate_title()
        self.___validate_description()
        self.___validate_color()

    def ___validate_title(self):
        if self.___title is None:
            return
        if not re.match(r'^[a-zA-Z0-9 ]{1,20}$', self.___title):
            raise ModelsAttributeError(
                "Title must be 20 characters or less and must contain only letters, numbers, and the special "
                "character: ''.")

    def ___validate_description(self):
        if self.___description is None:
            return
        if re.match(r"""^[a-zA-Z0-9 '".,;:!?-_()\n]{0,256}$""", self.___description) is None:
            raise ModelsAttributeError(
                "Description contains invalid characters or exceeds 256 characters. Accepted characters are "
                "letters, numbers, spaces, newlines, and the following special characters: '.', ',', ';', ':', '!', "
                "'?', '-', '', '(', ')'.")

    def ___validate_color(self):
        if self.___color is None:
            return
        if not re.match(r'^#[0-9A-Fa-f]{6}$', self.___color):
            raise ModelsAttributeError("Color must be in the format #RRGGBB (hexadecimal).")


class CardValidations:
    def __init__(self, **kwargs):
        self.___title = kwargs.get('card_title', None) or kwargs.get('title', None)
        self.___description = kwargs.get('card_description', None) or kwargs.get('description', None)
        self.___story_points = kwargs.get('story_points', None)
        self.___color = kwargs.get('color', None)

    def result(self):
        self.___validate_title()
        self.___validate_description()
        self.___validate_color()

    def ___validate_title(self):
        if self.___title is None:
            return
        if not re.match(r'^[a-zA-Z0-9 ]{1,20}$', self.___title):
            raise ModelsAttributeError(
                "Title must be 20 characters or less and must contain only letters, numbers, and the special "
                "character: ''.")

    def ___validate_description(self):
        if self.___description is None:
            return
        if re.match(r"""^[a-zA-Z0-9 '".,;:!?\-_()\n]{0,256}$""", self.___description) is None:
            raise ModelsAttributeError(
                "Description contains invalid characters or exceeds 256 characters. Accepted characters are "
                "letters, numbers, spaces, newlines, and the following special characters: '.', ',', ';', ':', '!', "
                "'?', '-', '', '(', ')'.")

    def ___validate_color(self):
        if self.___color is None:
            return
        if not re.match(r'^#[0-9A-Fa-f]{6}$', self.___color):
            raise ModelsAttributeError("Color must be in the format #RRGGBB (hexadecimal).")

    def ___validate_story_points(self):
        if self.___story_points is None:
            return
        if self.___story_points < 0 or self.___story_points > 16:
            raise ModelsAttributeError("Story points must be a number between 0 and 999.")

