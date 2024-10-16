import unittest
from unittest import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile

from authentication.models import User
from database import DBRequestBuilder, DBHybridTable, _FormatError, _meta_model as meta_model
from static.services import ModelsAttributeError
from static.services.validations import BoardValidations, CardValidations


class TestDBHybridTable(TestCase):

    def setUp(self):
        condition = "id=1"

        self.inner_table_1 = DBHybridTable("inner_table_1", "inner_table_2", condition)
        self.inner_table_2 = DBHybridTable("inner_table_3", "inner_table_4", condition)

        self.table_with_strings = DBHybridTable("table_1", "table_2", condition)
        self.table_with_mixed_inner_tables = DBHybridTable("table_1", self.inner_table_2, condition)
        self.table_with_only_inner_tables = DBHybridTable(self.inner_table_1, self.inner_table_2, condition)

    def test_init_with_empty_string(self):
        self.assertRaises(_FormatError, lambda: DBHybridTable("", "table_2", "id=1"))

    def test_table(self):
        actual = f"{meta_model("table_1")} JOIN ({meta_model("inner_table_3")} JOIN {meta_model("inner_table_4")} ON id=1) ON id=1"
        self.assertEqual(actual, self.table_with_mixed_inner_tables.table())

    def test_join(self):
        actual = f"({meta_model("table_1")} JOIN {meta_model("table_2")} ON id=1) JOIN ({meta_model("table_1")} JOIN {meta_model("table_2")} ON id=1) ON id=2"
        self.assertEqual(actual, self.table_with_strings.join(self.table_with_strings, "id=2").table())


class DBRequestBuilderTest(unittest.TestCase):

    def setUp(self):
        self.builder: DBRequestBuilder = DBRequestBuilder("test", "Error message")
        self.params = {
            "a": "name",
            "b": "id"
        }

    def test_message(self):
        self.assertEqual(self.builder.message(), "Error message")

    def test_name(self):
        self.assertEqual(self.builder.name(), "test")

    def test_query_with_empty_kwargs_and_query(self):
        self.assertRaises(_FormatError, self.builder.query)

    def test_query_with_kwargs_and_empty_query(self):
        self.assertRaises(_FormatError, lambda: self.builder.query(**self.params))

    def test_query_with_kwargs_and_query(self):
        self.builder.complex("SELECT PARAM(a), PARAM(b)")
        self.assertEqual("SELECT name, id\n", self.builder.query(**self.params))

    def test_select(self):
        self.builder.select("name", "age", "city")
        self.assertEqual("SELECT name, age, city\n", self.builder.query())

    def test_insert(self):
        self.builder.insert("citizens", "name", "age")
        self.assertEqual("INSERT INTO " + meta_model("citizens") + " name, age\n", self.builder.query())

    def test_insert_with_empty_string(self):
        self.assertRaises(_FormatError, lambda: self.builder.insert(""))

    def test_insert_with_empty_args(self):
        self.assertRaises(_FormatError, lambda: self.builder.insert("citizens"))

    def test_insert_with_hybrid_table(self):
        actual = "INSERT INTO " + meta_model("citizens") + " JOIN " + meta_model("cars") + " ON citizens_id=1 name, age\n"
        table = DBHybridTable("citizens", "cars", "citizens_id=1")
        self.builder.insert(table, "name", "age")
        self.assertEqual(actual, self.builder.query())

    def test_values(self):
        self.builder.values("Stefano", 25)
        self.assertEqual("VALUES Stefano, 25\n", self.builder.query())

    def test_from_table(self):
        table = DBHybridTable("citizens", "cars", "citizens_id=1")
        self.builder.from_table(table)
        self.assertEqual("FROM " + meta_model("citizens") + " JOIN " + meta_model("cars") + " ON citizens_id=1\n", self.builder.query())

    def test_from_table_with_empty_table(self):
        self.assertRaises(_FormatError, lambda: self.builder.from_table(""))

    def test_where(self):
        self.builder.where("name='Stefano'")
        self.assertEqual("WHERE name='Stefano'\n", self.builder.query())

    def test_and(self):
        self.builder._and_("age=25")
        self.assertEqual("AND age=25\n", self.builder.query())

    def test_or(self):
        self.builder._or_("age=25")
        self.assertEqual("OR age=25\n", self.builder.query())

    def test_order_by(self):
        self.builder.order_by("name", "age")
        self.assertEqual("ORDER BY name, age\n", self.builder.query())

    def test_limit(self):
        self.builder.limit(5)
        self.assertEqual("LIMIT 5\n", self.builder.query())

    def test_offset(self):
        self.builder.offset(5)
        self.assertEqual("OFFSET 5\n", self.builder.query())

    def test_complex_with_empty_query(self):
        self.assertRaises(_FormatError, lambda: self.builder.complex(""))

    def test_complex_with_query(self):
        actual = "SELECT * FROM citizens\nWHERE name='Stefano'\n"
        self.builder.complex("SELECT * FROM citizens")  \
                    .complex("WHERE name='Stefano'")
        self.assertEqual(actual, self.builder.query())

class TestBoardValidations(unittest.TestCase):

    def test_validate_board_title_too_long(self):
        with self.assertRaises(ModelsAttributeError) as context:
            validator = BoardValidations(None, title="This title is definitely too long")
            validator.validatetitle()
        self.assertIn("Title must be 16 characters or less", str(context.exception))

    def test_validate_board_title_invalid_characters(self):
        with self.assertRaises(ModelsAttributeError) as context:
            validator = BoardValidations(None, title="Invalid#Title!")
            validator.validatetitle()
        self.assertIn("Title must not contain special characters", str(context.exception))

    def test_validate_board_description_too_long(self):
        long_description = "a" * 257  # Stringa di 257 caratteri
        with self.assertRaises(ModelsAttributeError) as context:
            validator = BoardValidations(None, description=long_description)
            validator.validate_description()
        self.assertIn("exceeds 256 characters", str(context.exception))

    def test_validate_board_description_invalid_characters(self):
        with self.assertRaises(ModelsAttributeError) as context:
            validator = BoardValidations(None, description="Invalid#Description!")
            validator.validate_description()
        self.assertIn("Description must not contain special characters", str(context.exception))


    def test_validate_board_image_size_too_large(self):
        large_image = SimpleUploadedFile("large_image.jpg", b"0" * (3*1024*1024 + 1), content_type="image/jpeg")
        with self.assertRaises(ModelsAttributeError) as context:
            validator = BoardValidations(None, image=large_image)
            validator._validate_image()
        self.assertIn("Image size must be less than 3MB.", str(context.exception))


    def test_validate_board_image_invalid_format(self):
        invalid_image = SimpleUploadedFile("image.txt", b"dummy data", content_type="text/plain")
        with self.assertRaises(ModelsAttributeError) as context:
            validator = BoardValidations(None, image=invalid_image)
            validator._validate_image()
        self.assertIn("Image must be in the format: jpeg, png or jpg.", str(context.exception))

    def test_validate_correct_board_title(self):
        try:
            validator = BoardValidations(None, title="Valid Title")
            validator.validatetitle()
        except ModelsAttributeError:
            self.fail("validatetitle() raised ModelsAttributeError unexpectedly")

    def test_validate_correct_board_description(self):
        try:
            validator = BoardValidations(None, description="Valid Description")
            validator.validate_description()
        except ModelsAttributeError:
            self.fail("validate_description() raised ModelsAttributeError unexpectedly")

class TestCardValidations(unittest.TestCase):

    def test_validate_card_title_too_long(self):
        with self.assertRaises(ModelsAttributeError) as context:
            validator = CardValidations(None, title="This title is definitely too long")
            validator.validate_title()
        self.assertIn("Title must be 20 characters or less", str(context.exception))

    def test_validate_card_title_invalid_characters(self):
        with self.assertRaises(ModelsAttributeError) as context:
            validator = CardValidations(None, title="Invalid#Title!")
            validator.validate_title()
        self.assertIn("Title must not contain special characters", str(context.exception))

    def test_validate_card_description_too_long(self):
        long_description = "a" * 257  # Stringa di 257 caratteri
        with self.assertRaises(ModelsAttributeError) as context:
            validator = CardValidations(None, description=long_description)
            validator.validatedescription()
        self.assertIn("exceeds 256 characters", str(context.exception))

    def test_validate_card_description_invalid_characters(self):
        with self.assertRaises(ModelsAttributeError) as context:
            validator = CardValidations(None, description="Invalid#Description!")
            validator.validatedescription()
        self.assertIn("Description must not contain special characters", str(context.exception))


    def test_validate_card_image_size_too_large(self):
        large_image = SimpleUploadedFile("large_image.jpg", b"0" * (3*1024*1024 + 1), content_type="image/jpeg")
        with self.assertRaises(ModelsAttributeError) as context:
            validator = CardValidations(None, image=large_image)
            validator.validate_image()
        self.assertIn("Image size must be less than 3MB.", str(context.exception))


    def test_validate_card_image_invalid_format(self):
        invalid_image = SimpleUploadedFile("image.txt", b"dummy data", content_type="text/plain")
        with self.assertRaises(ModelsAttributeError) as context:
            validator = CardValidations(None, image=invalid_image)
            validator.validate_image()
        self.assertIn("Image must be in the format: jpeg, png or jpg.", str(context.exception))

    def test_validate_color_invalid_format(self):
        with self.assertRaises(ModelsAttributeError) as context:
            validator = CardValidations(None, color="123456")
            validator.validate_color()
        self.assertIn("Color must be in the format #RRGGBB (hexadecimal).", str(context.exception))

        with self.assertRaises(ModelsAttributeError) as context:
            validator = CardValidations(None, color="#12345G")
            validator.validate_color()
        self.assertIn("Color must be in the format #RRGGBB (hexadecimal).", str(context.exception))

    def test_validate_color_correct_format(self):
        try:
            validator = CardValidations(None, color="#1A2B3C")
            validator.validate_color()  # Non deve sollevare eccezioni
        except ModelsAttributeError:
            self.fail("validate_color() raised ModelsAttributeError unexpectedly!")

    def test_validate_correct_card_title(self):
        try:
            validator = CardValidations(None, title="Valid Title")
            validator.validate_title()
        except ModelsAttributeError:
            self.fail("validatetitle() raised ModelsAttributeError unexpectedly")

    def test_validate_correct_card_description(self):
        try:
            validator = CardValidations(None, description="Valid Description")
            validator.validatedescription()
        except ModelsAttributeError:
            self.fail("validate_description() raised ModelsAttributeError unexpectedly")
