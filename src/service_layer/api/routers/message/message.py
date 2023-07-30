from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dal.postgres.models import Message
from dal.postgres.db import get_session
from src.dal.minio import MinioFilesRepository
from src.dal.minio import Buckets, S3Client, MinioSettings

router = APIRouter()


@router.post('/upload')
async def upload(user_id: UUID, stmt_id: UUID, name: str,
                    file: UploadFile = File(...),
                    db: AsyncSession = Depends(get_session)
                 ):
    query = select(Message)#.filter(Message.stmt_id == stmt_id)
    value = (await db.scalars(query)).all()

    settings = MinioSettings()
    s3 = S3Client(settings=settings)
    product_images_repository = MinioFilesRepository(
        bucket=Buckets.FILES,
        minio_client=s3,
        settings=settings,
    )
    return await product_images_repository.add(user_id, stmt_id, file, name)


@router.get('/download')
async def download(user_id: UUID, stmt_id: UUID, file_id: UUID, name: str):
    settings = MinioSettings()
    s3 = S3Client(settings=settings)
    product_images_repository = MinioFilesRepository(
        bucket=Buckets.FILES,
        minio_client=s3,
        settings=settings,
    )
    file = await product_images_repository.find(user_id, stmt_id, file_id)

    return Response(file.getvalue(),
                    headers={
                        "content-type": "application/octet-stream",
                        'Content-Disposition': f"attachment; filename='{name}'"
                    },
                    )