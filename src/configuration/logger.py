import logging
import os
from logging.handlers import RotatingFileHandler

from semantic_kernel.agents.orchestration.magentic import logger as magentic_logger

from src.configuration.settings import BASE_DIR, app_settings

# Log file path
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / "app.log"

# Configure logger
# Follows the format used in semantic_kernel.utils.logging but adds file logging
logging.basicConfig(
    format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3),
        logging.StreamHandler(),  # Also log to console, mostly for development
    ],
)

# Set the logging level for the default logger (which is the root logger)
default_logger = logging.getLogger(__name__)
default_logger.setLevel(logging.DEBUG)

# Set the logging level for  semantic_kernel.kernel to DEBUG.
logging.getLogger("kernel").setLevel(logging.DEBUG)
magentic_logger.setLevel(logging.DEBUG)

# Set tracing
# LangSmith tracing is handles in environment variables
# so we only need to make sure the environment is set up correctly
if app_settings.langsmith_tracing:
    os.environ["LANGCHAIN_TRACING"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = app_settings.langsmith_endpoint
    os.environ["LANGCHAIN_API_KEY"] = app_settings.langsmith_api_key._secret_value
    os.environ["LANGCHAIN_PROJECT"] = app_settings.langsmith_project
