from abc import ABC
from dataclasses import dataclass

from dal.minio.client import S3Client, MinioSettings, Buckets


@dataclass()
class MinioRepository(ABC):
    minio_client: S3Client
    settings: MinioSettings
    bucket: Buckets
