import datetime
import json
import os
from pathlib import Path

from cli_parsing import parse_args
from connecting import S3Connection
from connecting.errors import ObjectNotFound
from errors import MissingEnvVariable
from extracting import DataSaver, DBSchema, SQLiteExtractor
from logger import Logger


METADETA_S3_PATH = Path("metadata/watch_table_checkpoints.json")
METADATA_SAVE_PATH = Path("./checkpoints.json")
DB_SAVE_PATH = Path("./saved.db")
EXTRACTED_DIR_PATH = Path("extracted_watch_tables")


def main() -> None:
    Logger.debug("Getting env variables")
    s3_endpoint = os.getenv("S3_ENDPOINT")
    if s3_endpoint is None:
        raise MissingEnvVariable("S3_ENDPOINT")

    s3_access_key = os.getenv("S3_ACCESS_KEY")
    if s3_access_key is None:
        raise MissingEnvVariable("S3_ACCESS_KEY")

    s3_secret_key = os.getenv("S3_SECRET_KEY")
    if s3_secret_key is None:
        raise MissingEnvVariable("S3_SECRET_KEY")

    Logger.debug("Creating S3 connection")
    s3_connection = S3Connection(s3_endpoint, s3_access_key, s3_secret_key)

    Logger.debug("Parsing CLI args")
    args = parse_args()

    Logger.info("Starting extraction")
    s3_connection.download_file(args.bucket, args.object_path, DB_SAVE_PATH)
    try:
        s3_connection.download_file(args.bucket, METADETA_S3_PATH, METADATA_SAVE_PATH)

        with open(METADATA_SAVE_PATH, "rb") as f:
            text_object = f.read().decode("utf-8")
        timestamps = json.loads(text_object)
        Logger.info("Loaded timestamps")
    except ObjectNotFound:
        Logger.warning("Timestamp object not found, timestamp cutoff will be 0")
        timestamps = {}
    except Exception as e:
        Logger.error(f"Error while trying to download timestamps: {e}")
        raise

    Logger.debug("Parsing schema from params")
    db_schema = DBSchema.from_cli_params(args.table, timestamps)

    extractor = SQLiteExtractor(DB_SAVE_PATH, db_schema)
    saver = DataSaver(EXTRACTED_DIR_PATH)

    Logger.info("Parsing tables")
    checkpoints = {}
    cest_tz = datetime.timezone(datetime.timedelta(hours=2))
    file_name = datetime.datetime.now(tz=cest_tz).strftime("%Y-%m-%dT%H:%M")
    for table_cursor, table_name, table_columns in extractor.extract_tables():
        data = table_cursor.fetchall()

        timestamp = saver.save_sqlite_result(data, table_columns, table_name, file_name)
        checkpoints[table_name] = timestamp

    Logger.info("Writing parsed tables to S3")
    s3_connection.write_dir(args.bucket, EXTRACTED_DIR_PATH)

    Logger.info("Uploading checkpoints")
    with open(METADATA_SAVE_PATH, "wb") as f:
        f.write(json.dumps(checkpoints).encode("utf-8"))
    try:
        s3_connection.write_file(args.bucket, str(METADETA_S3_PATH), METADATA_SAVE_PATH)
    except Exception as e:
        Logger.error(f"Error while writing checkpoints to S3: {e}")
        raise
    Logger.info("Done")


if __name__ == "__main__":
    main()
