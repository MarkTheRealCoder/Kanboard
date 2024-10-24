import unittest

from django.core.files.uploadedfile import SimpleUploadedFile

from static.services import ModelsAttributeError
from static.services.validations import BoardValidations, CardValidations, UserValidations


class TestUserValidations(unittest.TestCase):


    def test_validate_user_name_ok(self):
        validator = UserValidations(name="Validname")
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_user_name_too_long(self):
        validator = UserValidations(name="This name is definitely too long")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_user_name_invalid_characters(self):
        validator = UserValidations(name="Invalid#Name!")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_user_surname_ok(self):
        validator = UserValidations(surname="Valid surname")
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_user_surname_too_long(self):
        validator = UserValidations(surname="This surname is definitely too long")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_user_surname_invalid_characters(self):
        validator = UserValidations(surname="Invalid#Surname!")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_user_email_ok(self):
        validator = UserValidations(email="ex.amp.le@example.com")
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_user_email_invalid_format(self):
        validator = UserValidations(email="invalid_email")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_user_username_ok(self):
        validator = UserValidations(username="valid_username")
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_user_username_too_long(self):
        validator = UserValidations(username="this_username_is_definitely_too_long")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_user_username_invalid_characters(self):
        validator = UserValidations(username="invalid#username")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_user_password_ok(self):
        validator = UserValidations(password="valid_password")
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_user_password_too_short(self):
        validator = UserValidations(password="short")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_user_password_too_long(self):
        validator = UserValidations(password="this_password_is_definitely_too_long")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_user_password_invalid_characters(self):
        validator = UserValidations(password="invalid#password")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_user_image_ok(self):
        image = SimpleUploadedFile("image.jpg", b"dummy data", content_type="image/jpeg")
        validator = UserValidations(image=image)
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_user_image_size_too_large(self):
        image = SimpleUploadedFile("large_image.jpg", b"0" * (3*1024*1024 + 1), content_type="image/jpeg")
        validator = UserValidations(image=image)
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_user_image_invalid_format(self):
        image = SimpleUploadedFile("image.txt", b"dummy data", content_type="text/plain")
        validator = UserValidations(image=image)
        self.assertRaises(ModelsAttributeError, validator.result)



class TestBoardValidations(unittest.TestCase):


    def test_validate_board_title_ok(self):
        validator = BoardValidations(title="Valid title")
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_board_title_too_long(self):
        validator = BoardValidations(title="This title is definitely too long")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_board_title_invalid_characters(self):
        validator = BoardValidations(title="Invalid#Title!")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_board_description_ok(self):
        validator = BoardValidations(description="Valid description")
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_board_description_too_long(self):
        validator = BoardValidations(description=("a" * 257))
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_board_description_invalid_characters(self):
        validator = BoardValidations(description="Invalid#Description!")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_board_image_ok(self):
        image = SimpleUploadedFile("image.jpg", b"dummy data", content_type="image/jpeg")
        validator = BoardValidations(image=image)
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_board_image_size_too_large(self):
        image = SimpleUploadedFile("large_image.jpg", b"0" * (3*1024*1024 + 1), content_type="image/jpeg")
        validator = BoardValidations(image=image)
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_board_image_invalid_format(self):
        image = SimpleUploadedFile("image.txt", b"dummy data", content_type="text/plain")
        validator = BoardValidations(image=image)
        self.assertRaises(ModelsAttributeError, validator.result)



class TestCardValidations(unittest.TestCase):


    def test_validate_card_title_ok(self):
        validator = CardValidations(title="Valid title")
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_card_title_too_long(self):
        validator = CardValidations(title="This title is definitely too long")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_card_title_invalid_characters(self):
        validator = CardValidations(title="Invalid#Title!")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_card_description_ok(self):
        validator = CardValidations(description="Valid description")
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_card_description_too_long(self):
        validator = CardValidations(description=("a" * 257))
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_card_description_invalid_characters(self):
        validator = CardValidations(description="Invalid#Description!")
        self.assertRaises(ModelsAttributeError, validator.result)


    def test_validate_card_color_ok(self):
        validator = CardValidations(color="#1A2B3C")
        try:
            validator.result()
        except ModelsAttributeError as e:
            self.fail(f"result() raised ModelsAttributeError unexpectedly: {e}")


    def test_validate_color_invalid_format(self):
        validator = CardValidations(color="123456")
        self.assertRaises(ModelsAttributeError, validator.result)


if __name__ == '__main__':
    unittest.main()