"""LangChain chat model for Credit Intelligence."""

from functools import lru_cache

from langchain_anthropic import ChatAnthropic

from config import settings


@lru_cache(maxsize=None)
def chat_model(max_tokens: int = 500) -> ChatAnthropic:
    return ChatAnthropic(model=settings.anthropic_model,api_key=settings.anthropic_api_key,max_tokens=max_tokens,timeout=30.0,max_retries=3)