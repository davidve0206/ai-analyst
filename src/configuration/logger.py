import logging
from logging.handlers import RotatingFileHandler
from src.configuration.settings import BASE_DIR

# Log file path
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / "app.log"

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3),
        logging.StreamHandler(),  # Also log to console, mostly for development
    ],
)

logger = logging.getLogger(__name__)
