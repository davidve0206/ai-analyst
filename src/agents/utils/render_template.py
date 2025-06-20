from jinja2 import Environment, FileSystemLoader

from src.configuration.settings import BASE_DIR


def render_prompt(template_name: str, context: dict) -> str:
    """
    Renders a Jinja2 template with the given context.

    Args:
        template_name (str): The name of the template file to render.
        context (dict): A dictionary containing the context variables for the template.

    Returns:
        str: The rendered template as a string.
    """
    prompts_path = BASE_DIR / "src" / "agents" / "prompts"
    jinja_env = Environment(loader=FileSystemLoader(prompts_path))
    template = jinja_env.get_template(template_name)
    return template.render(context)
