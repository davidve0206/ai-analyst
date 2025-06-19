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
    # Allows None in case the user wants to log in with a different method
    # such as azure cli. NOTE: the app will fail if the user never authenticates.
    azure_tenant_id: str | None = None
    azure_client_id: str | None = None
    azure_client_secret: str | None = None

    # Database settings
    azure_db_server: str
    azure_db_database: str
    azure_db_connection_timeout: int = 30

    model_config = ConfigDict(extra="ignore")


CONFIG_FILE_PATH = BASE_DIR / ".env"
app_settings = Settings(_env_file=CONFIG_FILE_PATH)
