import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "民族志纪录片剪辑会议系统"
    API_V1_PREFIX: str = "/api/v1"

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")

    PYANNOTE_AUTH_TOKEN: str = os.getenv("PYANNOTE_AUTH_TOKEN", "")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./montage.db")

    # 可测性改造：上传目录可通过环境变量配置，默认行为不变。
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")

    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def openai_configured(self) -> bool:
        return bool((self.OPENAI_API_KEY or "").strip())

    @property
    def pyannote_configured(self) -> bool:
        return bool((self.PYANNOTE_AUTH_TOKEN or "").strip())

    @property
    def smtp_configured(self) -> bool:
        return bool((self.SMTP_USER or "").strip()) and bool((self.SMTP_PASSWORD or "").strip())


settings = Settings()
