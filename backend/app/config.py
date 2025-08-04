import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    TIDB_USER: str
    TIDB_PASSWORD: str
    TIDB_HOST: str
    TIDB_PORT: int
    TIDB_DB: str
    DATABASE_URL: str = ""

    class Config:
        env_file = ".env"

    def __init__(self, **values):
        super().__init__(**values)
        self.DATABASE_URL = (
            f"mysql+mysqldb://{self.TIDB_USER}:{self.TIDB_PASSWORD}"
            f"@{self.TIDB_HOST}:{self.TIDB_PORT}/{self.TIDB_DB}"
        )

settings = Settings()
