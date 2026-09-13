import argparse
from cli_parsing.errors import MissingCLIArgument


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="SQLite S3 Extractor",
        description="downloads SQLite file from S3 storage and uploads parquet files with extracted tables",
    )

    mode_group = parser.add_argument_group("mode")
    mode_group.add_argument(
        "mode",
        choices=["extract", "update"],
        help="extract for turning S3 stored SQLite file into S3 stored parquet files, update for overwriting a file stored on S3",
    )

    s3_group = parser.add_argument_group("s3")
    s3_group.add_argument("-b", "--bucket", help="S3 bucket where the data is stored")

    extract_group = parser.add_argument_group("extract")
    extract_group.add_argument("-op", "--object-path", help="path to the file on S3")
    extract_group.add_argument(
        "-wp",
        "--write-path",
        help="path to the S3 where the extracted files will be written",
    )
    extract_group.add_argument(
        "-t",
        "--table",
        action="append",
        help="table to be extracted in the format 'table_name:column1,column2...'",
    )

    update_group = parser.add_argument_group("update")
    update_group.add_argument(
        "-c",
        "--checkpoint",
        help="a JSON object with timestamps for each table that will be saved on S3",
    )

    args = parser.parse_args()

    _validate_cli_args(args)

    return args


def _validate_cli_args(args: argparse.Namespace):
    if args.bucket is None:
        raise MissingCLIArgument("--bucket (-b)")

    match args.mode:
        case "extract":
            # op, wp, table
            if args.object_path is None:
                raise MissingCLIArgument("--object_path (-op)")

            if args.write_path is None:
                raise MissingCLIArgument("--write_path (-wp)")

            if args.table is None:
                raise MissingCLIArgument("--table (-t)")
        case "update":
            if args.checkpoint is None:
                raise MissingCLIArgument("--checkpoint (-c)")
