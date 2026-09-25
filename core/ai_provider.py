"""Minimal HTTP clients for DeepSeek text and a configurable vision provider."""
import json
from typing import Any, Dict, Optional

import aiohttp

from bot.config import (
    AI_REQUEST_TIMEOUT,
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    DEEPSEEK_TEXT_MODEL,
    DEEPSEEK_VISION_MODEL,
)


class AIProviderError(RuntimeError):
    pass


def _headers(api_key: str) -> Dict[str, str]:
    return {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}


async def chat_completion(
    messages: list[Dict[str, Any]],
    *,
    temperature: float = 0.3,
    max_tokens: int = 1500,
    vision: bool = False,
) -> str:
    api_key = DEEPSEEK_API_KEY
    api_url = DEEPSEEK_API_URL
    model = DEEPSEEK_VISION_MODEL if vision else DEEPSEEK_TEXT_MODEL
    if not api_key:
        provider = 'DeepSeek Vision' if vision else 'DeepSeek'
        raise AIProviderError(f'{provider} API key is not configured')

    payload = {
        'model': model,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }
    timeout = aiohttp.ClientTimeout(total=AI_REQUEST_TIMEOUT)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(api_url, headers=_headers(api_key), json=payload) as response:
                body = await response.text()
                if response.status >= 400:
                    try:
                        detail = json.loads(body).get('error', {}).get('message', body)
                    except json.JSONDecodeError:
                        detail = body
                    raise AIProviderError(f'AI provider returned {response.status}: {detail[:500]}')
                data = json.loads(body)
                content = data.get('choices', [{}])[0].get('message', {}).get('content')
                if isinstance(content, list):
                    content = ''.join(part.get('text', '') for part in content if isinstance(part, dict))
                if not content:
                    raise AIProviderError('AI provider returned an empty response')
                return str(content)
    except aiohttp.ClientError as error:
        raise AIProviderError(f'AI provider connection failed: {error}') from error
