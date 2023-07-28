from enum import Enum

import boto3
from botocore.client import Config
from mypy_boto3_s3 import S3Client
from mypy_boto3_s3.service_resource import Bucket

from .config import MinioSettings

s3_settings = MinioSettings()

s3_client: S3Client = boto3.client(
    "s3",
    endpoint_url=s3_settings.URL,
    aws_access_key_id=s3_settings.access_token,
    aws_secret_access_key=s3_settings.secret_key,
    config=Config(signature_version="s3v4"),
)


class Buckets(str, Enum):
    FILES = "files"


# _existed_buckets = [bucket["Name"] for bucket in s3_client.list_buckets()["Buckets"]]
# for bucket in Buckets:
#     if bucket.value not in _existed_buckets:
#         s3_client.create_bucket(Bucket=bucket.value)


class S3Client:

    def __init__(self, settings: MinioSettings) -> None:
        self.s3 = boto3.resource(
            "s3",
            endpoint_url=settings.URL,
            aws_access_key_id=settings.access_token,
            aws_secret_access_key=settings.secret_key,
            config=Config(signature_version="s3v4"),
        )
        self.products: Bucket = self[Buckets.FILES]

    def __getitem__(self, item: str) -> Bucket:
        return self.s3.Bucket(item)
