from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder

from app.models import Message
from app.api import deps
from pydantic import BaseModel

from app.dal.minio import MinioFilesRepository
from app.dal.minio import Buckets, S3Client, MinioSettings

router = APIRouter()


class MessageFormField(BaseModel):
    text: str
    stmt: UUID
    from_: UUID
    to: UUID


@router.post("/post")
async def chat(
        message: MessageFormField,
        db: AsyncSession = Depends(deps.get_session),
):
    """add current chat"""
    _message = Message(
        text=message.text,
        stmt_id=message.stmt,
        user_id=message.to
    )
    db.add(_message)
    try:
        await db.commit()
    except Exception as e:
        return e

    return _message


@router.get('/load')
async def get_chat(stmt: UUID = None, user_id: UUID = None,
                   db: AsyncSession = Depends(deps.get_session)):
    query = select(Message)
    if stmt is not None:
        query = query.where(Message.stmt_id == stmt)
    if user_id is not None:
        query = query.where(Message.user_id == user_id)


    res = (await db.scalars(query)).all()
    test = jsonable_encoder(res[0])
    return res


@router.post('/upload')
async def upload(user_id: UUID, stmt_id: UUID, name: str,
                    file: UploadFile = File(...),
                    db: AsyncSession = Depends(deps.get_session)
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