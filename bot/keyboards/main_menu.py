from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from bot.config import WEBAPP_PUBLIC_URL


def _web_app_button():
    """Telegram accepts WebAppInfo only with a public HTTPS URL."""
    if WEBAPP_PUBLIC_URL.startswith('https://'):
        return InlineKeyboardButton(
            text="🚀 Открыть Gym Helper",
            web_app=WebAppInfo(url=WEBAPP_PUBLIC_URL.rstrip('/')),
        )
    return InlineKeyboardButton(text="🌐 Mini App: настрой HTTPS", callback_data="app_setup")


def get_main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [_web_app_button()],
        [InlineKeyboardButton(text="📊 Калькуляторы", callback_data="calculators"), InlineKeyboardButton(text="📸 Сканировать", callback_data="scan_food")],
        [InlineKeyboardButton(text="💊 Добавки", callback_data="supplements"), InlineKeyboardButton(text="👤 Профиль", callback_data="my_profile")],
        [InlineKeyboardButton(text="📈 Мой прогресс", callback_data="weight_history"), InlineKeyboardButton(text="📋 Программы", callback_data="programs_soon")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
