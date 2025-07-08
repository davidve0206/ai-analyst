import matplotlib
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import EmailStr, ConfigDict, SecretStr

BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
OUTPUTS_DIR = BASE_DIR / "outputs"
TEMP_DIR = OUTPUTS_DIR / "temp"
STORAGE_DIR = OUTPUTS_DIR / "storage"
CACHE_DIR = OUTPUTS_DIR / "cache"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    # Email settings
    email_from_address: EmailStr = "test@test.com"
    email_username: str | None
    email_password: SecretStr | None
    email_host: str
    email_port: int
    email_use_ssl: bool

    # Azure identity settings
    # Allows None in case the user wants to log in with a different method
    # such as azure cli. NOTE: the app will fail if the user never authenticates.
    azure_tenant_id: str | None = None
    azure_client_id: str | None = None
    azure_client_secret: SecretStr | None = None

    # Database settings
    azure_db_server: str
    azure_db_database: str
    azure_db_connection_timeout: int = 30

    # Model settings
    gemini_api_key: SecretStr | None = None
    azure_foundry_project_endpoint: str | None = None
    azure_openai_api_key: SecretStr | None = None
    azure_openai_endpoint: str | None = None

    # Observability settings
    langsmith_tracing: bool = False
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_api_key: SecretStr | None = None
    langsmith_project: str = "default"

    model_config = ConfigDict(extra="ignore")


CONFIG_FILE_PATH = BASE_DIR / ".env"
app_settings = Settings(_env_file=CONFIG_FILE_PATH)


# Ensure all required directories exist
def ensure_directories_exist():
    """Create all required directories if they don't exist."""
    directories = [
        OUTPUTS_DIR,
        TEMP_DIR,
        STORAGE_DIR,
        CACHE_DIR,
        LOG_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# Create directories on import
ensure_directories_exist()

# Ensure matplotlib uses a non-interactive backend
matplotlib.use("Agg")