from pydantic import BaseSettings


class MinioSettings(BaseSettings):
    URL: str = "http://127.0.0.1:9000"
    access_token: str = "superadmin123"
    secret_key: str = "superadmin123"
    public_host: str = "0.0.0.0"
    public_port: int = 9001
    ssl: bool = False

    class Config:
        env_prefix = "minio_"
