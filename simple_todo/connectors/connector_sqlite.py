import sqlite3
from datetime import datetime

from .connector_base import Connector


class SqliteConnector(Connector):
    def __init__(self, database_path: str):
        self.database_path = database_path

        self.connection: sqlite3.Connection | None = None

        self._connect()
        self._initialize_database()

    def _initialize_database(self):
        create_query = """
            CREATE TABLE IF NOT EXISTS 
                todos 
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    text TEXT, 
                    due_date date
                )
        """

        cursor = self.connection.cursor()
        try:
            cursor.execute(create_query)
            self.connection.commit()
        finally:
            cursor.close()

    def _connect(self):
        self.connection = sqlite3.connect(self.database_path)

    def _insert(self, insert_query: str, params: list | tuple):
        cursor = self.connection.cursor()
        try:
            cursor.execute(insert_query, params)
            self.connection.commit()
        finally:
            cursor.close()

    def _select(self, query: str, params: list | tuple = None):
        if not params:
            params = []

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            for entry in cursor.fetchall():
                yield entry
        finally:
            cursor.close()

    def add_todo(self, text: str, due_date: datetime.date):
        insert_query = """
        INSERT INTO
            todos (text, due_date)
        VALUES 
            (?, ?)
        """

        self._insert(insert_query, [text, due_date])

    def list_todos(self):
        select_query = """
            SELECT
                *
            FROM
                todos
            WHERE
             due_date >= date('now') 
            ORDER BY
                due_date
        """

        return self._select(select_query)
