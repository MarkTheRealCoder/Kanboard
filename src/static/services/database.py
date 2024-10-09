import re
import sqlite3

def _meta_model(table: str):
    """
    Returns a formatted table name that can be easily parsed to generate correct SQL queries' elements.
    """
    return f"<table:{table}>"

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


class DBHybridField:
    """
    Represents a parameter in a SQL query that can be used to substitute values dynamically.
    :param table: str - The name of the table.
    :param field: str - The name of the parameter.

    This class translates many python comparison operations to SQL comparison operations:\n
    - == translates to = or IS NULL if the value is None
    - != translates to != or IS NOT NULL if the value is None
    - < translates to <
    - <= translates to <=
    - > translates to >
    - >= translates to >=

    Example:
        ```field = DBHybridField("table", "field")```\n
        ```print(field == 10) # Output: table.field = 10```
    """
    def __init__(self, table: int, field: int):
        self.___field = _meta_model(table) + "." + field

    def __str__(self):
        return self.___field

    def __repr__(self):
        return self.___field

    def __eq__(self, value):
        return f"{self.___field} = {str(value)}" if value is not None else f"{self.___field} IS NULL"

    def __ne__(self, value):
        return f"{self.___field} != {str(value)}" if value is not None else f"{self.___field} IS NOT NULL"

    def __lt__(self, value):
        return f"{self.___field} < {str(value)}"

    def __le__(self, value):
        return f"{self.___field} <= {str(value)}"

    def __gt__(self, value):
        return f"{self.___field} > {str(value)}"

    def __ge__(self, value):
        return f"{self.___field} >= {str(value)}"


class DBHybridTable:
    """
    Represents a complex table in a SQL query by facilitating the creation of SQL JOINs.

    This class allows the combination of two tables with a specified join condition.
    It also supports chaining multiple joins for building more complex SQL queries.

    :param table1: str | DBHybridTable - The primary table or an instance of DBHybridTable for nested joins.
    :param table2: str | DBHybridTable - The secondary table or another instance of DBHybridTable.
    :param condition: str - The SQL condition that defines how the two tables should be joined.
    """

    def __init__(self, table1: str or 'DBHybridTable', table2: str or 'DBHybridTable', condition: str):
        """
        Initializes the DBHybridTable with the given tables and join condition.

        :param table1: str | DBHybridTable - The primary table or an instance of DBHybridTable for nested joins.
        :param table2: str | DBHybridTable - The secondary table or another instance of DBHybridTable.
        :param condition: str - The SQL condition that defines how the two tables should be joined.
        """
        self.___is_complex_table1: bool = not isinstance(table1, str)
        self.___is_complex_table2: bool = not isinstance(table2, str)

        self._table_name: str = self._get_table_name(table1, self.___is_complex_table1)
        self._join_table_name: str = self._get_table_name(table2, self.___is_complex_table2)
        self.___condition: str = condition

    def _get_table_name(self, table: str or 'DBHybridTable', is_complex: bool) -> str:
        """
        Returns the table name, handling complex table cases.

        :param table: str | DBHybridTable - The table to get the name for.
        :param is_complex: bool - Whether the table is a complex table.
        :return: str - The table name.
        """
        if not table:
            raise _FormatError("Table name cannot be empty or `None`")

        return f"({table.table()})" if is_complex else _meta_model(table)

    def table(self) -> str:
        """
        Returns the SQL representation of the joined tables.

        :return: str - A string representing the SQL JOIN clause.
        """
        return f"{self._table_name} JOIN {self._join_table_name} ON {self.___condition}"

    def join(self, table: str or 'DBHybridTable', condition: str) -> 'DBHybridTable':
        """
        Creates a new DBHybridTable by joining the current table with another table.

        :param table: str | DBHybridTable - The table to join with.
        :param condition: str - The SQL condition for the join.
        :return: DBHybridTable - A new instance of DBHybridTable representing the joined tables.
        """
        return DBHybridTable(self, table, condition)


class _WhereCondition:
    """
    Represents a condition in an SQL query where specific arguments can be substituted dynamically.

    This class allows the definition of a condition with placeholders, which can be later replaced
    by actual values passed to the `apply_condition` method.

    :param condition: str - A string representing the condition with placeholders for arguments in the form of PARAM(n).
    """

    def __init__(self, condition: str):
        """
        Initializes the WhereCondition with the given condition string.

        :param condition: str - A string representing the condition with placeholders for arguments in the form of PARAM(n).
        """
        if not condition:
            raise _FormatError("Condition string cannot be empty or `None`")

        self.___condition: str = condition

    def get_condition(self) -> str:
        """
        Returns the condition string with placeholders.

        :return: str - The condition string.
        """
        return self.___condition

    def condition(self, **kwargs) -> str:
        """
        Replaces the placeholders in the condition string with the provided arguments.

        :param kwargs: tuple - The arguments to replace the placeholders.
        :return: str - The condition string with placeholders replaced by the provided arguments.
        """
        return self.___parse_condition(**kwargs)

    def ___parse_condition(self, **kwargs) -> str:
        """
        Internal method to replace placeholders in the condition string with the provided arguments.

        :param kwargs: tuple - The arguments to replace the placeholders.
        :return: str - The condition string with placeholders replaced by the provided arguments.
        :raises FormatError: If an invalid argument name is encountered.
        """
        condition_copy = self.___condition
        for i in re.findall("PARAM\\(([A-Za-z_]+[A-Za-z0-9_]*)\\)", condition_copy):
            if i not in kwargs.keys():
                raise _FormatError(f"Invalid argument: {i} is not part of the function arguments")
            condition_copy = condition_copy.replace(f"PARAM({i})", str(kwargs.get(i)))
        return condition_copy


class _DBQuery:
    """
    This class is used to represent a query.
    This class is not directly usable or accessible from the user, it is used by the DBRequestBuilder class to build the query.

    The query is built by calling the various methods of this class.
    """

    def __init__(self):
        """
        Initializes the DBQuery with an empty query string.
        """
        self.___query: str = ""

    def ___add(self, query: str):
        """
        Adds a query string to the current query.

        :param query: str - The query string to add.
        """
        if not query:
            raise _FormatError("Query string cannot be empty or `None`")

        self.___query += (query + "\n")

    def select(self, *args):
        """
        Adds a SELECT clause to the query.

        :param args: tuple - The columns to select.
        """
        arguments: list[str] = [str(i) for i in args]
        self.___add("SELECT " + ", ".join(arguments))

    def insert(self, table: str or DBHybridTable, *args):
        """
        Adds an INSERT clause to the query.

        :param table: str | DBHybridTable - The table to insert into.
        :param args: tuple - The columns to insert.
        """
        arguments: list[str] = [str(i) for i in args]
        table_name = table if isinstance(table, str) else table.table()
        self.___add(f"INSERT INTO {table_name} " + ", ".join(arguments))

    def values(self, *args):
        """
        Adds a VALUES clause to the query.

        :param args: tuple - The values to insert.
        """
        arguments: list[str] = [str(i) for i in args]
        self.___add("VALUES " + ", ".join(arguments))

    def from_table(self, table: str or DBHybridTable):
        """
        Adds a FROM clause to the query.

        :param table: str | DBHybridTable - The table to select from.
        """
        table_name = table if isinstance(table, str) else table.table()
        self.___add(f"FROM {table_name}")

    def where(self, condition: str):
        """
        Adds a WHERE clause to the query.

        :param condition: str - The condition for the WHERE clause.
        """
        self.___add("WHERE " + condition)

    def _and(self, condition: str):
        """
        Adds an AND clause to the query.

        :param condition: str - The condition for the AND clause.
        """
        self.___add("AND " + condition)

    def _or(self, condition: str):
        """
        Adds an OR clause to the query.

        :param condition: str - The condition for the OR clause.
        """
        self.___add("OR " + condition)

    def order_by(self, *args):
        """
        Adds an ORDER BY clause to the query.

        :param args: tuple - The columns to order by.
        """
        arguments: list[str] = [str(i) for i in args]
        self.___add("ORDER BY " + ", ".join(arguments))

    def limit(self, limit: int):
        """
        Adds a LIMIT clause to the query.

        :param limit: int - The maximum number of rows to return.
        """
        self.___add("LIMIT " + str(limit))

    def offset(self, offset: int):
        """
        Adds an OFFSET clause to the query.

        :param offset: int - The number of rows to skip before starting to return rows.
        """
        self.___add("OFFSET " + str(offset))

    def complex(self, value: str):
        """
        Adds a custom query string to the query.

        :param value: str - The custom query string to add.
        """
        self.___add(value)

    def query(self, **kwargs) -> str:
        """
        Returns the final query string with placeholders replaced by the provided arguments.

        :param kwargs: tuple - The arguments to replace the placeholders.
        :return: str - The final query string.
        :raises FormatError: If the query string is empty.
        """
        if not self.___query:
            raise _FormatError("Empty query")

        return _WhereCondition(self.___query).condition(**kwargs)


class DBRequestBuilder:
    """
    This class is used to build a query.

    The query is built by calling the various methods of this class and chaining them together.
    The first method to be called must be the select method, followed by the fromTable method, other methods are optional.

    For more complex queries you can use the complex method to add a custom query or a custom element
    to the query that was being built.

    The full query is returned by calling the query method.

    :param error_message: str - The error message to be returned in case of an error

    :tip: The query method returns a WhereCondition object that can be used to replace the arguments in the condition with the values passed to the condition method.
    """
    def __init__(self, _name: str, error_message: str):
        """
        Initializes the DBRequestBuilder with an error message.

        :param error_message: str - The error message to be returned in case of an error.
        """
        self.___query: _DBQuery = _DBQuery()
        self.___name = _name
        self.___error_message = error_message

    def message(self) -> str:
        """
        Returns the error message.

        :return: str - The error message.
        """
        return self.___error_message

    def name(self) -> str:
        """
        Returns the name of the parameter.

        :return: str - The name of the parameter.
        """
        return self.___name

    def query(self, **kwargs) -> str:
        """
        Returns the final query string with placeholders replaced by the provided arguments.

        :param kwargs: tuple - The arguments to replace the placeholders.
        :return: str - The final query string.
        """
        return self.___query.query(**kwargs)

    def select(self, *args) -> 'DBRequestBuilder':
        """
        Adds a SELECT clause to the query.

        :param args: tuple - The columns to select.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        self.___query.select(*args)
        return self

    def insert(self, table: str or DBHybridTable, *args) -> 'DBRequestBuilder':
        """
        Adds an INSERT clause to the query.

        :param table: str | DBHybridTable - The table to insert into.
        :param args: tuple - The columns to insert.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        if not table:
            raise _FormatError("Table name cannot be empty or `None`")

        if not args:
            raise _FormatError("Columns to insert cannot be empty or `None`")

        if not isinstance(table, DBHybridTable):
            table = _meta_model(table)
        self.___query.insert(table, *args)
        return self

    def values(self, *args) -> 'DBRequestBuilder':
        """
        Adds a VALUES clause to the query.

        :param args: tuple - The values to insert.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        self.___query.values(*args)
        return self

    def from_table(self, table: str or DBHybridTable) -> 'DBRequestBuilder':
        """
        Adds a FROM clause to the query.

        :param table: str | DBHybridTable - The table to select from.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        if not table:
            raise _FormatError("Table name cannot be empty or `None`")

        if not isinstance(table, DBHybridTable):
            table = _meta_model(table)
        self.___query.from_table(table)
        return self

    def where(self, condition: str) -> 'DBRequestBuilder':
        """
        Adds a WHERE clause to the query.

        :param condition: str - The condition for the WHERE clause.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        self.___query.where(condition)
        return self

    def _and_(self, condition: str) -> 'DBRequestBuilder':
        """
        Adds an AND clause to the query.

        :param condition: str - The condition for the AND clause.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        self.___query._and(condition)
        return self

    def _or_(self, condition: str) -> 'DBRequestBuilder':
        """
        Adds an OR clause to the query.

        :param condition: str - The condition for the OR clause.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        self.___query._or(condition)
        return self

    def order_by(self, *args) -> 'DBRequestBuilder':
        """
        Adds an ORDER BY clause to the query.

        :param args: tuple - The columns to order by.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        self.___query.order_by(*args)
        return self

    def limit(self, limit: int) -> 'DBRequestBuilder':
        """
        Adds a LIMIT clause to the query.

        :param limit: int - The maximum number of rows to return.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        self.___query.limit(limit)
        return self

    def offset(self, offset: int) -> 'DBRequestBuilder':
        """
        Adds an OFFSET clause to the query.

        :param offset: int - The number of rows to skip before starting to return rows.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        self.___query.offset(offset)
        return self

    def complex(self, value: str) -> 'DBRequestBuilder':
        """
        Adds a custom query string to the query.

        :param value: str - The custom query string to add.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        self.___query.complex(value)
        return self


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
            value = _DBReference.___databases.get(database, None)
            value = value.get(model_name, None)
        except Exception as e:
            del e
            raise_error = True

        if raise_error:
            raise _ModelError("The required table does not exist or is not mapped.")

        return value


register = _DBReference.register


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
        with sqlite3.connect(self.___db_path) as conn:
            try:
                value = conn.cursor().execute(query).fetchall()
            except sqlite3.Error as e:
                raise _DatabaseError(f"An error occurred: {e}")
        return value
