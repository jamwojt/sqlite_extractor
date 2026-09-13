import boto3


class S3Connection:
    def __init__(
        self, s3_endpoint: str, s3_access_key: str, s3_secret_key: str
    ) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=s3_endpoint,
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key,
        )

    def download_file(self, bucket: str, s3_path: str, save_path: str) -> None:
        response = self.client.get_object(Bucket=bucket, Key=s3_path)
        status = response.get("HTTPStatusCode")
        print(type(status))
        print(response)
        # if status is None or status != 200:
        #     raise DownloadFailed

        contents = response["Body"].read()

        with open(save_path, "wb") as f:
            f.write(contents)

    def write_file(self, bucket: str, s3_path: str, file_path: str) -> None:
        with open(file_path, "rb") as f:
            self.client.put_object(Bucket=bucket, Key=s3_path, Body=f.read())
