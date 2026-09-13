from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Self

    from pyarrow import Table


@dataclass
class TableInfo:
    name: str
    columns: list[str]
    timestamp_column: str
    timestamp: int

    def __init__(self, name: str, timestamp: int, *columns: tuple[str]) -> None:
        self.name = name
        self.timestamp = timestamp
        self.timestamp_column = columns[0]
        self.columns = list(columns)

    def __post_init__(self):
        if self.name is None or len(self.name) == 0:
            raise ValueError("Name is missing")
        if self.columns is None or len(self.columns) == 0:
            raise ValueError("Column names are missing")
        if self.timestamp_column is None or self.timestamp_column == "":
            raise ValueError("Timestamp column name is missing")
        if self.timestamp is None or self.timestamp <= 0:
            raise ValueError("Invalid timestamp")


class DBSchema:
    tables: list[TableInfo]

    def __init__(self, tables: dict[str, TableInfo]):
        self.tables = tables

    @classmethod
    def from_cli_params(cls, table_list: list[str], timestamps: dict[str, int]) -> Self:
        tables = (t.split(":") for t in table_list)
        tables = [TableInfo(t[0], timestamps[t[0]], *(t[1].split(","))) for i, t in enumerate(tables)]

        return cls(tables)


class SQLiteExtractor:
    def __init__(self, connection_string: str, schema: DBSchema):
        self.con = sqlite3.connect(connection_string)
        self.schema = schema

    def extract_tables(self) -> Generator[tuple[str, Table]]:
        cursor = self.con.cursor()

        query = """
        SELECT ? FROM ? WHERE ? > ?;
        """

        for table in self.schema:
            columns = ", ".join(table.columns)
            result = cursor.execute(
                query, (columns, table.name, table.timestamp_column, table.timestamp)
            )

            yield result
