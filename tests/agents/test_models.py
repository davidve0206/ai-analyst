import pytest
from src.agents.models import AppChatModels


@pytest.mark.asyncio
async def test_gemini_2_0_client_connects(models_client: AppChatModels):
    invoke_result = await models_client.gemini_2_0_flash.ainvoke(
        [{"role": "user", "content": "What is the capital of Paris?"}]
    )
    assert "Paris" in invoke_result.content


@pytest.mark.asyncio
async def test_openai_gpt_4o_mini_client_connects(models_client: AppChatModels):
    invoke_result = await models_client.openai_gpt_4o_mini.ainvoke(
        [{"role": "user", "content": "What is the capital of France?"}]
    )
    assert "Paris" in invoke_result.content


@pytest.mark.asyncio
async def test_openai_o4_mini_client_connects(models_client: AppChatModels):
    invoke_result = await models_client.openai_o4_mini.ainvoke(
        [{"role": "user", "content": "What is the capital of France?"}]
    )
    assert "Paris" in invoke_result.content
