import re
import sqlite3
from uuid import UUID


class _FormatError(Exception):
    """
    Represents an error that occurs if the desired format cannot be implemented.
    """
    pass


class _DatabaseError(Exception):
    """
    Represents an error that occurs during database operations.
    """
    pass


class _ModelError(_DatabaseError):
    """
    Represents an error that occurs if the model is not found.
    """
    pass


class DBTable:
    """
    This class is used to create a parsable table for the queries in the database.

    The join method is used to join two tables in the SQL query.
    The field method is used to specify the field in the SQL query.

    You cannot use both the join method and the field method in the same instance.
    """

    def __init__(self, table: str):
        self.___table = f"_{table}_"

    def join(self, table: 'DBTable', condition: str) -> '_DBTable':
        self.___table = f"({self.___table} JOIN {table} ON {condition})"
        return self

    def field(self, field: str) -> str:
        return f"{self.___table}.{field}"

    def __str__(self):
        return f"{self.___table}"


class _DBTable:
    def __init__(self, table: str):
        self.___table = table

    def join(self, table: 'DBTable' or '_DBTable', condition: str) -> '_DBTable':
        self.___table = f"({self.___table} JOIN {table} ON {condition})"
        return self

    def __str__(self):
        return f"{self.___table}"


class DBQuery:
    def __init__(self, _name: str, error_message: str):
        self.___name = _name
        self.___error_message = error_message
        self.___select = "*"
        self.___from = ""
        self.___where = ""

    def filter(self, condition="", **kwargs):
        """
        Creates a WHERE clause in the SQL query based on the given parameters.
        You can use both a kwarg or an unpacked dictionary to pass the parameters.

        When you are making a simple query, you can use the following syntax:
        DBQuery(...).filter(name="John", age=20)

        If you are making a query with join clauses or where you need to specify which tables owns the field, you can use the following syntax:
        DBQuery(...).filter(_table_name="John", _table_age=20)
        """
        where = []
        for key, value in kwargs.items():
            where.append(f"{key} = {value}")
        self.___where = condition + " AND ".join(where)
        return self

    def only(self, *args):
        """
        Selects only the specified columns in the SQL query.
        You can use both a single argument or multiple arguments to pass the columns.
        For specific columns when using join clauses, you can use the following syntax:
        DBQuery(...).only(DBTable("table", "name"), DBField("table", "age"))
        """
        self.___select = ", ".join([str(arg) for arg in args])
        return self

    def from_table(self, table: str or DBTable):
        """
        Specifies the table in the SQL query.
        You can use both a string or a DBTable instance to pass the table.

        For simple queries, you can use the following syntax:
        DBQuery(...).from_table("table")
        """
        self.___from = f"_{table}_" if isinstance(table, str) else str(table)
        return self

    def query(self, **kwargs):
        query = f"SELECT {self.___select} FROM {self.___from}"
        if self.___where:
            query += f" WHERE {self.___where}"
        return self.___parse_param(query, **kwargs)

    def ___parse_param(self, query: str, **kwargs):
        """
        Parses the parameters in the query.
        :param query: str - The query string to parse.
        :param kwargs: dict - The arguments to parse.
        :return: str - The parsed query
        """
        condition_copy = query
        for i in re.findall("PARAM\\(([A-Za-z_]+[A-Za-z0-9_]*)\\)", condition_copy):
            if i not in kwargs.keys():
                raise _FormatError(f"Invalid argument: {i} is not part of the function arguments")
            value = self.___value_type_parse(kwargs.get(i))
            if value is None:
                value = "NULL"
            condition_copy = condition_copy.replace(f"PARAM({i})", str(value))
        return condition_copy

    def ___value_type_parse(self, value):
        if value is None:
            return None
        parsed = str(value)
        if isinstance(value, bool):
            parsed = parsed.upper()
        elif isinstance(value, str):
            parsed = f"'{parsed}'"
        return parsed

    @property
    def name(self):
        """
        Returns the name of the result of the query.
        """
        return self.___name

    @property
    def message(self):
        """
        Returns the error message of the DBQuery instance.
        """
        return self.___error_message



class _DBReference:
    """
    This class is used to store the mapping of models.

    The register method is used to register the model in the mapping storage.
    The find method is used to find the model in the mapping storage.

    The register method is a decorator that takes the database name and the app name as input.
    """
    ___databases: dict[str: dict[str: str]] = {}

    @staticmethod
    def register(database: str, app_name: str):
        """
        Registers the model in the mapping storage.

        :param database: str - The name of the database.
        :param app_name: str - The name of the app.
        """

        def wrapper(clazz):
            class_name = str(clazz.__name__).lower()
            references = _DBReference.___databases.get(database, dict())
            if not database in _DBReference.___databases.keys():
                _DBReference.___databases[database] = references
            references[class_name] = f"{app_name.lower()}_{class_name}"
            return clazz

        return wrapper

    @staticmethod
    def find(database: str, model_name: str):
        """
        Finds the model in the mapping storage.

        :param database: str - The name of the database.
        :param model_name: str - The name of the model.
        :return: str - The name of the model in the database.
        :raises ModelError: If the model is not found.
        """
        raise_error = False
        value = None

        try:
            value = _DBReference.___databases.get(database)
            value = value.get(model_name.lower())
        except Exception as e:
            del e
            raise_error = True

        if raise_error:
            raise _ModelError("The required table does not exist or is not mapped.")

        return value


register = _DBReference.register
DEBUG_ENABLED = True

class _DBServices:
    """
    This class is used to execute a query and establish a connection to the database (SQLite ONLY).

    The execute method is used to execute a query and takes a string as input.
    """

    def __init__(self, db_path: str):
        """
        Initializes the DBServices class.
        :param db_path: str - The path to the database file.
        """
        self.___db_path: str = db_path

    def execute(self, query: str) -> list:
        """
        Executes the given query string.

        :param query: str - The query string to execute.
        :return: Any - The result of the query execution.
        """
        value = None
        query = self.___parse_table(query)
        with sqlite3.connect(self.___db_path) as conn:
            try:
                if DEBUG_ENABLED:
                    print("[DEBUG] Executing query: " + query)
                value = conn.cursor().execute(query).fetchall()
            except sqlite3.Error as e:
                raise _DatabaseError(f"An error occurred: {e}")
        return value

    def ___parse_table(self, query: str):
        """
        Parses the table names in the query.
        :param query: str - The query string to parse.
        :return: str - The parsed query
        """
        condition_copy = query
        for i in re.findall("_([A-Za-z_]+[A-Za-z0-9_]*)_([A-Za-z_]+[A-Za-z0-9_]*)", condition_copy): # Fields
            model = _DBReference.find(self.___db_path, i[0])
            condition_copy = condition_copy.replace(f"_{i[0]}_{i[1]}", f"{model}.{i[1]}")

        for i in re.findall("_([A-Za-z_]+[A-Za-z0-9_]*)_", condition_copy):                          # Tables
            model = _DBReference.find(self.___db_path, i)
            condition_copy = condition_copy.replace(f"_{i}_", model)
        return condition_copy