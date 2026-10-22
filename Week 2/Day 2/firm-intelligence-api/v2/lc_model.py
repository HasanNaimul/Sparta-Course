"""LangChain chat model configured to match the native Anthropic client in llm.py.

Existing llm.py decisions:
- 30 second timeout
- 3 retries
"""

from functools import lru_cache

from langchain_anthropic import ChatAnthropic

import llm


@lru_cache(maxsize=None)
def chat_model(max_tokens: int = 500) -> ChatAnthropic:
    return ChatAnthropic(model=llm.MODEL, max_tokens=max_tokens, timeout=30.0, max_retries=3)