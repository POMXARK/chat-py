import io
from uuid import uuid4, UUID

from starlette import status
from starlette.responses import JSONResponse

from .abc import MinioRepository


class MinioFilesRepository(MinioRepository):

    async def add(self, user_id: UUID, stmt_id: UUID, file, name: str):
        file_id = uuid4()
        _file = file.file.read()
        self.minio_client.products.put_object(
            Body=io.BytesIO(_file),
            Key=f"{stmt_id}/{user_id}/{file_id}",
            ACL="public-read",
        )

        data = {}
        data['name'] = name
        data['file_id'] = str(file_id)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            headers={"location": f"/download?user_id={user_id}"
                                 f"stmt_id={stmt_id}"
                                 f"file_id={file_id}"
                                 f"name={name}"
                     },
            content= data
        )

    async def find(self, user_id: UUID, stmt_id: UUID, file_id: UUID) -> io.BytesIO:
        file_obj = io.BytesIO()
        self.minio_client.products.download_fileobj(
            Key=f"{stmt_id}/{user_id}/{file_id}",
            Fileobj=file_obj,
        )
        return file_obj
