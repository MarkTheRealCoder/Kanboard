import unittest
from unittest import TestCase

from database import DBRequestBuilder, DBHybridTable, _FormatError


class TestDBHybridTable(TestCase):

    def setUp(self):
        condition = "id=1"

        self.inner_table_1 = DBHybridTable("inner_table_1", "inner_table_2", condition)
        self.inner_table_2 = DBHybridTable("inner_table_3", "inner_table_4", condition)

        self.table_with_strings = DBHybridTable("table_1", "table_2", condition)
        self.table_with_mixed_inner_tables = DBHybridTable("table_1", self.inner_table_2, condition)
        self.table_with_only_inner_tables = DBHybridTable(self.inner_table_1, self.inner_table_2, condition)

    def tearDown(self):
        pass

    def test_set_app_with_appname_empty(self):
        self.assertRaises(_FormatError, lambda: self.table_with_strings.set_app(""))

    def test_set_app_with_strings_check_table_name(self):
        actual = "myapp_table_1"
        self.table_with_strings.set_app("myapp")
        self.assertEqual(actual, self.table_with_strings._table_name)

    def test_set_app_with_strings_check_join_table_name(self):
        actual = "myapp_table_2"
        self.table_with_strings.set_app("myapp")
        self.assertEqual(actual, self.table_with_strings._join_table_name)

    def test_set_app_with_mixed_mocks_check_table_name(self):
        actual = "myapp_table_1"
        self.table_with_mixed_inner_tables.set_app("myapp")
        self.assertEqual(actual, self.table_with_mixed_inner_tables._table_name)

    def test_set_app_with_mixed_mocks_check_join_table_name(self):
        actual = "(inner_table_3 JOIN inner_table_4 ON id=1)"
        self.table_with_mixed_inner_tables.set_app("myapp")
        self.assertEqual(actual, self.table_with_mixed_inner_tables._join_table_name)

    def test_set_app_with_only_mocks_check_table_name(self):
        actual = "(inner_table_1 JOIN inner_table_2 ON id=1)"
        self.table_with_only_inner_tables.set_app("myapp")
        self.assertEqual(actual, self.table_with_only_inner_tables._table_name)

    def test_set_app_with_only_mocks_check_join_table_name(self):
        actual = "(inner_table_3 JOIN inner_table_4 ON id=1)"
        self.table_with_only_inner_tables.set_app("myapp")
        self.assertEqual(actual, self.table_with_only_inner_tables._join_table_name)

    def test_init_with_empty_string(self):
        self.assertRaises(_FormatError, lambda: DBHybridTable("", "table_2", "id=1"))

    def test_table(self):
        actual = "table_1 JOIN (inner_table_3 JOIN inner_table_4 ON id=1) ON id=1"
        self.assertEqual(actual, self.table_with_mixed_inner_tables.table())

    def test_join(self):
        actual = "(table_1 JOIN table_2 ON id=1) JOIN (table_1 JOIN table_2 ON id=1) ON id=2"
        self.assertEqual(actual, self.table_with_strings.join(self.table_with_strings, "id=2").table())


class DBRequestBuilderTest(unittest.TestCase):

    def setUp(self):
        self.builder: DBRequestBuilder = DBRequestBuilder("testapp", "test", "Error message")
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
        self.assertEqual("INSERT INTO testapp_citizens name, age\n", self.builder.query())

    def test_insert_with_empty_string(self):
        self.assertRaises(_FormatError, lambda: self.builder.insert(""))

    def test_insert_with_empty_args(self):
        self.assertRaises(_FormatError, lambda: self.builder.insert("citizens"))

    def test_insert_with_hybrid_table(self):
        actual = "INSERT INTO testapp_citizens JOIN testapp_cars ON citizens_id=1 name, age\n"
        table = DBHybridTable("citizens", "cars", "citizens_id=1")
        self.builder.insert(table, "name", "age")
        self.assertEqual(actual, self.builder.query())

    def test_values(self):
        self.builder.values("Stefano", 25)
        self.assertEqual("VALUES Stefano, 25\n", self.builder.query())

    def test_from_table(self):
        table = DBHybridTable("citizens", "cars", "citizens_id=1")
        self.builder.from_table(table)
        self.assertEqual("FROM testapp_citizens JOIN testapp_cars ON citizens_id=1\n", self.builder.query())

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

