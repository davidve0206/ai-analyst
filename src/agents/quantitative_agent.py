from azure.ai.projects.aio import AIProjectClient
from semantic_kernel.agents import AzureAIAgent
from azure.ai.agents.models import CodeInterpreterTool

from src.agents.models import AzureOpenAIModels, ModelTypes
from src.agents.tools.projections import ProjectionsPlugin
from src.agents.utils.prompt_utils import render_prompt_from_jinja


async def create_quantitative_agent(
    azure_ai_client: AIProjectClient,
    model_type: ModelTypes = ModelTypes.AZURE_OPENAI,
) -> AzureAIAgent:
    """
    Create an instance of the QuantitativeAgent with the Code Interpreter tool.
    """
    code_interpreter = CodeInterpreterTool()
    system_prompt = render_prompt_from_jinja("quantitative_agent_system_prompt.md.j2")

    if model_type == ModelTypes.AZURE_OPENAI:
        agent_definition = await azure_ai_client.agents.create_agent(
            model=AzureOpenAIModels.GPT_4o_MINI.value,
            name="QuantitativeAgent",
            description="An agent that can analyze, project and plot data using the Code Interpreter tool.",
            instructions=system_prompt,
            tools=code_interpreter.definitions,
            tool_resources=code_interpreter.resources,
        )
        agent = AzureAIAgent(
            client=azure_ai_client,
            definition=agent_definition,
            plugins=[ProjectionsPlugin()],
        )

        return agent
    else:
        raise ValueError(f"Unsupported model type for coder agent: {model_type}")
