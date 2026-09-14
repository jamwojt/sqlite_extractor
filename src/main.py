import json
import os
from pathlib import Path

import pyarrow
from dotenv import load_dotenv

from cli_parsing import parse_args
from cli_parsing.errors import MissingCLIArgument
from connecting import S3Connection
from connecting.errors import DownloadFailed, ObjectNotFound
from extracting import DataSaver, DBSchema, SQLiteExtractor


METADETA_S3_PATH = Path("metadata/table_checkpoints.json")
DB_SAVE_PATH = Path("./saved.db")
METADATA_SAVE_PATH = Path("./checkpoints.json")


def main() -> None:
    load_dotenv()
    s3_endpoint = os.getenv("S3_ENDPOINT")
    s3_access_key = os.getenv("S3_ACCESS_KEY")
    s3_secret_key = os.getenv("S3_SECRET_KEY")

    s3_connection = S3Connection(s3_endpoint, s3_access_key, s3_secret_key)

    args = parse_args()
    match args.mode:
        case "extract":
            s3_connection.download_file(args.bucket, args.object_path, DB_SAVE_PATH)
            try:
                s3_connection.download_file(
                    args.bucket, METADETA_S3_PATH, METADATA_SAVE_PATH
                )

                timestamps = json.loads(Path("./checkpoints.json"))
            except ObjectNotFound:
                timestamps = {}

            db_schema = DBSchema.from_cli_params(args.table, timestamps)

            extractor = SQLiteExtractor(DB_SAVE_PATH, db_schema)
            saver = DataSaver(Path("extracted"))

            for table_cursor, table_name, table_columns in extractor.extract_tables():
                data = table_cursor.fetchall()

                saver.save_sqlite_result(data, table_columns, table_name)
        case "update":
            s3_connection.write_file(args.bucket, METADETA_S3_PATH, METADATA_SAVE_PATH)


if __name__ == "__main__":
    main()
