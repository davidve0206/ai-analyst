import pytest
from src.agents.models import AppChatModels


@pytest.mark.asyncio
async def test_gemini_2_0_client_connects(models_client: AppChatModels):
    invoke_result = await models_client.gemini_2_0_flash.ainvoke(
        [{"role": "user", "content": "What is the capital of Paris?"}]
    )
    assert "Paris" in invoke_result.content


@pytest.mark.asyncio
async def test_gemini_2_5_pro_client_connects(models_client: AppChatModels):
    invoke_result = await models_client.gemini_2_5_pro.ainvoke(
        [{"role": "user", "content": "What is the capital of France?"}]
    )
    assert "Paris" in invoke_result.content


@pytest.mark.asyncio
async def test_gpt_o4_mini_client_connects(models_client: AppChatModels):
    invoke_result = await models_client.gpt_o4_mini.ainvoke(
        [{"role": "user", "content": "What is the capital of France?"}]
    )
    assert "Paris" in invoke_result.content
