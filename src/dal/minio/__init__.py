from dependency_injector import containers, providers

from .client import Buckets, S3Client
from .config import MinioSettings
from .repositories import *


class Container(containers.DeclarativeContainer):
    settings = MinioSettings()
    s3 = providers.Singleton(S3Client, settings=settings)
    product_images = providers.Factory(
        MinioFilesRepository,
        minio_client=s3,
        settings=settings,
        bucket=Buckets.FILES,
    )
