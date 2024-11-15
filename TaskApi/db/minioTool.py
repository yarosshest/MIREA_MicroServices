from fastapi import UploadFile
from minio import Minio
from io import BytesIO

from db.models import Photo
from models.models import PdPhoto


class MinioApi:
    client: Minio

    def __init__(self):
        self.client = Minio("78.136.223.100:9000",
                            access_key="zCfPQXd4TpxllgqBzjXV",
                            secret_key="JFxiH6acdNuCReZzTik8VVhseqvHy6oVq89j06Uq",
                            secure=False
                            )

    async def put_task_photo(self, file: UploadFile, unique_filename: str):
        byt = BytesIO(await file.read())
        # Загрузка файла в MinIO
        self.client.put_object(
            "task-photo",
            unique_filename,
            byt,
            file.size
        )

    def convertFromDbPhoto(self, db_photos: list[Photo]) -> list[PdPhoto]:
        res = []
        for i in db_photos:
            url = self.client.presigned_get_object(
                'task-photo',
                i.filename)
            res.append(PdPhoto(id=i.id, url=url))
        return res


minioApi = MinioApi()
