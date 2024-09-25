import re
import sqlite3
from sqlite3 import Connection

from _ctypes import FormatError


class _DatabaseError(Exception):
    """
    Represents an error that occurs during database operations.
    """
    pass


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
        self.___complex: list[bool] = [not isinstance(table1, str), not isinstance(table2, str)]
        self.___table_name: str = table1 if not self.___complex[0] else f"({table1.table()})"
        self.___join_table: str = table2 if not self.___complex[1] else f"({table2.table()})"
        self.___condition: str = condition

    def set_app(self, app_name: str):
        """
        Sets the application name for the table.

        :param app_name: str - The name of the application.
        """
        if not self.___complex[0]:
            self.___table_name = f"{app_name}_{self.___table_name}"
        if not self.___complex[1]:
            self.___join_table = f"{app_name}_{self.___join_table}"

    def table(self) -> str:
        """
        Returns the SQL representation of the joined tables.

        :return: str - A string representing the SQL JOIN clause.
        """
        return f"{self.___table_name} JOIN {self.___join_table} ON {self.___condition}"

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

        :param args: tuple - The arguments to replace the placeholders.
        :return: str - The condition string with placeholders replaced by the provided arguments.
        """
        return self.___parse_condition(**kwargs)

    def ___parse_condition(self, **kwargs) -> str:
        """
        Internal method to replace placeholders in the condition string with the provided arguments.

        :param args: tuple - The arguments to replace the placeholders.
        :return: str - The condition string with placeholders replaced by the provided arguments.
        :raises FormatError: If an invalid argument name is encountered.
        """
        condition_copy = self.___condition
        for i in re.findall("PARAM\\(([A-Za-z_]+[A-Za-z0-9_]*)\\)", condition_copy):
            if i not in kwargs.keys():
                raise FormatError(f"Invalid argument: {i} is not part of the function arguments")
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
        self.___query += (query + "\n")

    def select(self, *args):
        """
        Adds a SELECT clause to the query.

        :param args: tuple - The columns to select.
        """
        arguments: list[str] = [str(i) for i in args]
        self.___add("SELECT " + ", ".join(arguments))

    def fromTable(self, table: str or DBHybridTable):
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
        self.___add(str(limit))

    def offset(self, offset: int):
        """
        Adds an OFFSET clause to the query.

        :param offset: int - The number of rows to skip before starting to return rows.
        """
        self.___add(str(offset))

    def complex(self, value: str):
        """
        Adds a custom query string to the query.

        :param value: str - The custom query string to add.
        """
        self.___add(value)

    def query(self, **kwargs) -> str:
        """
        Returns the final query string with placeholders replaced by the provided arguments.

        :param args: tuple - The arguments to replace the placeholders.
        :return: str - The final query string.
        :raises FormatError: If the query string is empty.
        """
        if not self.___query:
            raise FormatError("Empty query")
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
    def __init__(self, app_name: str, _name: str, error_message: str):
        """
        Initializes the DBRequestBuilder with an error message.

        :param error_message: str - The error message to be returned in case of an error.
        """
        self.___app_name = app_name
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

        :param args: tuple - The arguments to replace the placeholders.
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

    def fromTable(self, table: str or DBHybridTable) -> 'DBRequestBuilder':
        """
        Adds a FROM clause to the query.

        :param table: str | DBHybridTable - The table to select from.
        :return: DBRequestBuilder - The DBRequestBuilder instance for chaining.
        """
        if isinstance(table, DBHybridTable):
            table.set_app(self.___app_name)
        else:
            table = f"{self.___app_name}_{table}"
        self.___query.fromTable(table)
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

    def execute(self, query: str):
        """
        Executes the given query string.

        :param query: str - The query string to execute.
        :return: Any - The result of the query execution.
        """
        print(self.___db_path)
        value = None
        with sqlite3.connect(self.___db_path) as conn:
            try:
                value = conn.cursor().execute(query).fetchall()
            except sqlite3.Error as e:
                raise _DatabaseError(f"An error occurred: {e}")
        if value == []:
            raise _DatabaseError("No results found.")
        return value


