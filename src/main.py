import json
import os
from pathlib import Path

from dotenv import load_dotenv

from cli_parsing import parse_args
from connecting import S3Connection
from connecting.errors import DownloadFailed, ObjectNotFound
from errors import MissingEnvVariable
from extracting import DataSaver, DBSchema, SQLiteExtractor
from logger import Logger


METADETA_S3_PATH = Path("metadata/table_checkpoints.json")
DB_SAVE_PATH = Path("./saved.db")
METADATA_SAVE_PATH = Path("./checkpoints.json")
EXTRACTED_DIR_PATH = Path("")


def main() -> None:
    load_dotenv()
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
    match args.mode:
        case "extract":
            Logger.info("Starting extraction")
            s3_connection.download_file(args.bucket, args.object_path, DB_SAVE_PATH)
            try:
                s3_connection.download_file(
                    args.bucket, METADETA_S3_PATH, METADATA_SAVE_PATH
                )

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
            for table_cursor, table_name, table_columns in extractor.extract_tables():
                data = table_cursor.fetchall()

                saver.save_sqlite_result(data, table_columns, table_name)

            Logger.info("Writing parsed tables to S3")
            s3_connection.write_dir(args.bucket, EXTRACTED_DIR_PATH)
            Logger.info("Done")
        case "update":
            Logger.info("Starting update")
            try:
                Logger.info("Parsing the passed object")
                json.loads(args.checkpoint)
            except json.JSONDecodeError:
                Logger.info("Invalid JSON object")
                return
            Logger.info("Uploading object")
            with open(METADATA_SAVE_PATH, "wb") as f:
                f.write(args.checkpoint.encode("utf-8"))
            s3_connection.write_file(args.bucket, str(METADETA_S3_PATH), METADATA_SAVE_PATH)


if __name__ == "__main__":
    main()
