from jinja2 import Environment, FileSystemLoader
from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from semantic_kernel.prompt_template import PromptTemplateConfig, Jinja2PromptTemplate


from src.configuration.settings import BASE_DIR

PROMPTS_PATH = BASE_DIR / "src" / "agents" / "prompts"


async def render_prompt_from_yml_template(
    template_name: str, context: dict, kernel: Kernel | None = None
) -> str:
    """
    DO NOT USE: This function follows the documentation but there is an error;
    only included in case Microsoft fixes the issue in the future.

    Creates a default Semantic Kernel instance with the necessary configurations
    loaded from the settings.

    Returns:
        str: The rendered prompt as a string.

    """

    if not kernel:
        kernel = Kernel()

    yaml_path = PROMPTS_PATH / template_name
    with open(yaml_path, "r") as f:
        yaml_content = f.read()

    prompt_template_config = PromptTemplateConfig.from_yaml(yaml_content)
    prompt_template = Jinja2PromptTemplate(
        prompt_template_config=prompt_template_config
    )
    arguments = KernelArguments(**context)
    return await prompt_template.render(kernel, arguments)

def render_prompt_from_jinja(template_name: str, context: dict = {}) -> str:
    """
    Renders a Jinja2 template with the given context.

    Args:
        template_name (str): The name of the template file to render.
        context (dict): A dictionary containing the context variables for the template.

    Returns:
        str: The rendered template as a string.
    """
    jinja_env = Environment(loader=FileSystemLoader(PROMPTS_PATH))
    template = jinja_env.get_template(template_name)
    return template.render(context)
