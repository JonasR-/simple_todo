import datetime


class Connector:
    def add_todo(self, text: str, due_date: datetime.date | str) -> str | int:
        raise NotImplemented

    def list_todos(self) -> list:
        raise NotImplemented
