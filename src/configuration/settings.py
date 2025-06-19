from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import EmailStr, ConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Email settings
    email_from_address: EmailStr = "test@test.com"
    email_username: str | None
    email_password: str | None
    email_host: str = "smtp.gmail.com"
    email_port: int = 465
    email_use_ssl: bool = False
    email_recipient: EmailStr = "test@test.com"

    # Azure identity settings
    azure_tenant_id: str
    azure_client_id: str
    azure_client_secret: str

    model_config = ConfigDict(extra="ignore")


CONFIG_FILE_PATH = BASE_DIR / ".env"
app_settings = Settings(_env_file=CONFIG_FILE_PATH)
