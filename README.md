# SQLite Extractor
Turns SQLite files on S3 into parquet files that can be picked up with spark.

## Env Variables
|name|description|
|----|-----------|
|S3_ENDPOINT|endpoint that the app should call to access S3|
|S3_ACCESS_KEY|access key for authenticating|
|S3_SECRET_KEY|secret key for authenticating|


# CLI Parameters
|name|flags|description|
|----|-----|-----------|
|mode|-|positional argument, either 'extract' or 'update'|
|bucket|-b, --bucket|bucket where the data lives|
|object path|-op --object_path|path to the object on S3|
|write path|-wp --write_path|directory where the parquet data will be saved|
|table|-t, --table|table to be extracted in the format 'table_name:timestamp_column,col1,col2...'|
|checkpoint|-c, --checkpoint|string JSON in the format '{"table_name": timestamp}' where timestamp is the unix timestamp of last processed record in the table|


