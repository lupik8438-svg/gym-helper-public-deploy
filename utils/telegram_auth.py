"""Validation of Telegram Mini App initData.

The browser never sends a user id as authority. When opened inside Telegram,
Telegram signs initData with the bot token and we verify that signature here.
"""
import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl
from typing import Dict, Optional

from bot.config import BOT_TOKEN


def validate_init_data(init_data: str, max_age_seconds: int = 86400) -> Optional[Dict]:
    if not init_data or not BOT_TOKEN:
        return None
    try:
        values = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = values.pop('hash', None)
        if not received_hash:
            return None
        data_check_string = '\n'.join(f'{key}={values[key]}' for key in sorted(values))
        secret_key = hmac.new(b'WebAppData', BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None
        auth_date = int(values.get('auth_date', '0'))
        if max_age_seconds and time.time() - auth_date > max_age_seconds:
            return None
        user = json.loads(values.get('user', '{}'))
        if not user.get('id'):
            return None
        return {'user': user, 'auth_date': auth_date}
    except (ValueError, TypeError, json.JSONDecodeError):
        return None
