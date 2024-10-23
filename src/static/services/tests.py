import unittest

from django.core.files.uploadedfile import SimpleUploadedFile

from static.services import ModelsAttributeError
from static.services.validations import BoardValidations, CardValidations


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

