from pathlib import Path

import pyarrow
import pyarrow.compute as pc
import pyarrow.parquet as pq


class DataSaver:
    save_root: Path

    def __init__(self, save_root: Path) -> None:
        self.save_root = save_root

    @staticmethod
    def _to_column_based(data: list[tuple]) -> list[list]:
        column_based_data = []
        for i in range(len(data[0])):
            column_data = [x[i] for x in data]
            column_based_data.append(pyarrow.array(column_data))

        return column_based_data

    @staticmethod
    def _create_pyarrow_table(column_data: list, columns: list[str]) -> pyarrow.Table:
        table = pyarrow.table(column_data, columns)

        return table

    def save_sqlite_result(
        self, data: list[tuple], columns: list[str], table_name: str, file_name: str
    ) -> None:
        column_based_data = DataSaver._to_column_based(data)
        timestamp = int(pc.max(column_based_data[0]))
        table = DataSaver._create_pyarrow_table(column_based_data, columns)

        save_path = self.save_root / Path(table_name) / Path(f"{file_name}.parquet")
        save_path.parent.mkdir(exist_ok=True, parents=True)
        save_path.touch(exist_ok=True)

        pq.write_table(table, save_path)

        return timestamp
