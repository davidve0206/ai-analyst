"""To be moved to the main config package if this becomes the main agent logging config."""

import logging
from logging.handlers import RotatingFileHandler

from src.configuration.settings import BASE_DIR

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
