import argparse

from cli_parsing.errors import MissingCLIArgument


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="SQLite S3 Extractor",
        description="downloads SQLite file from S3 storage and uploads parquet files with extracted tables",
    )

    parser.add_argument("-b", "--bucket", help="S3 bucket where the data is stored")

    parser.add_argument("-op", "--object-path", help="path to the file on S3")
    parser.add_argument(
        "-wp",
        "--write-path",
        help="path to the S3 where the extracted files will be written",
    )
    parser.add_argument(
        "-t",
        "--table",
        action="append",
        help="table to be extracted in the format 'table_name:column1,column2...'",
    )

    args = parser.parse_args()

    _validate_cli_args(args)

    return args


def _validate_cli_args(args: argparse.Namespace) -> None:
    if args.bucket is None:
        raise MissingCLIArgument("--bucket (-b)")

    if args.object_path is None:
        raise MissingCLIArgument("--object_path (-op)")

    if args.write_path is None:
        raise MissingCLIArgument("--write_path (-wp)")

    if args.table is None:
        raise MissingCLIArgument("--table (-t)")
