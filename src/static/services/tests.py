import unittest
from unittest import TestCase
from wsgiref.validate import validator

from static.services import ModelsAttributeError
from static.services.validations import UserValidations, ColumnValidations
from database import DBRequestBuilder, DBHybridTable, _FormatError, _meta_model as meta_model


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

    class TestUserValidations(unittest.TestCase):

        def create_image(self, size, content_type):
            return {
                'size': size,
                'content_type': content_type
            }

        def test_validate_username_too_long(self):
            validation = UserValidations(None, username="ThisUsernameIsWayTooLongForValidation12345")
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_username_invalid_characters(self):
            validation = UserValidations(None, username="Invalid!Username")
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_email_invalid_format(self):
            validation = UserValidations(None, email="invalidemail.com")
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_password_invalid(self):
            validation = UserValidations(None, password="short")
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_image_invalid_format(self):
            validation = UserValidations(None, image=self.create_image(1024 * 1024, 'image/gif'))
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_image_too_large(self):
            validation = UserValidations(None, image=self.create_image(5 * 1024 * 1024, 'image/jpeg'))
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_correct_username(self):
            try:
                validation = UserValidations(None, username="ValidUsername")
                validation.result()
            except ModelsAttributeError:
                self.fail("validate_username() raised ModelsAttributeError unexpectedly")

        def test_validate_correct_email(self):
            try:
                validation = UserValidations(None, email="valid_email@example.com")
                validation.result()
            except ModelsAttributeError:
                self.fail("validate_email() raised ModelsAttributeError unexpectedly")

        def test_validate_correct_password(self):
            try:
                validation = UserValidations(None, password="ValidPass123!")
                validation.result()
            except ModelsAttributeError:
                self.fail("validate_password() raised ModelsAttributeError unexpectedly")

        def test_validate_correct_image(self):
            try:
                validation = UserValidations(None, image=self.create_image(1024 * 1024, 'image/jpeg'))
                validation.result()
            except ModelsAttributeError:
                self.fail("validate_image() raised ModelsAttributeError unexpectedly")

    class TestColumnValidations(unittest.TestCase):

        def create_image(self, size, content_type):
            return {
                'size': size,
                'content_type': content_type
            }

        def test_validate_title_too_long(self):
            validation = ColumnValidations(title="This title is definitely too long")
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_title_invalid_characters(self):
            validation = ColumnValidations(title="Invalid title with !@#$%^")
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_description_too_long(self):
            validation = ColumnValidations(description='a' * 257)
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_description_invalid_characters(self):
            validation = ColumnValidations(description="Invalid description with & symbols")
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_color_invalid(self):
            validation = ColumnValidations(color="123456")
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_image_too_large(self):
            validation = ColumnValidations(image=self.create_image(4 * 1024 * 1024, 'image/jpeg'))
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_image_invalid_format(self):
            validation = ColumnValidations(image=self.create_image(1024 * 1024, 'image/gif'))
            self.assertRaises(ModelsAttributeError, validation.result)

        def test_validate_correct_title(self):
            try:
                validation = ColumnValidations(title="Valid Title")
                validation.result()
            except ModelsAttributeError:
                self.fail("validate_title() raised ModelsAttributeError unexpectedly")

        def test_validate_correct_description(self):
            try:
                validation = ColumnValidations(description="This is a valid description.")
                validation.result()
            except ModelsAttributeError:
                self.fail("validate_description() raised ModelsAttributeError unexpectedly")

        def test_validate_correct_color(self):
            try:
                validation = ColumnValidations(color="#1A2B3C")
                validation.result()
            except ModelsAttributeError:
                self.fail("validate_color() raised ModelsAttributeError unexpectedly")

        def test_validate_correct_image(self):
            try:
                validation = ColumnValidations(image=self.create_image(1024 * 1024, 'image/jpeg'))
                validation.result()
            except ModelsAttributeError:
                self.fail("validate_image() raised ModelsAttributeError unexpectedly")