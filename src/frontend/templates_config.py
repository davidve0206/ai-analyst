# Setup Jinja2 templates
from fastapi.templating import Jinja2Templates

from src.configuration.settings import SRC_DIR

templates_path = SRC_DIR / "frontend" / "templates"
templates = Jinja2Templates(directory=templates_path)
