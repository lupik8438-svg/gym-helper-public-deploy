from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from bot.config import WEBAPP_PUBLIC_URL


def _web_app_button():
    """Telegram accepts WebAppInfo only with a public HTTPS URL."""
    if WEBAPP_PUBLIC_URL.startswith('https://'):
        return InlineKeyboardButton(
            text="🚀 Открыть Gym Helper",
            web_app=WebAppInfo(url=WEBAPP_PUBLIC_URL.rstrip('/')),
        )
    return InlineKeyboardButton(text="🌐 Mini App пока не подключён", callback_data="app_setup")


def get_main_menu() -> InlineKeyboardMarkup:
    """Compact mobile-first home screen with clear app management/navigation."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [_web_app_button()],
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile"), InlineKeyboardButton(text="📈 Прогресс", callback_data="monthly_dashboard")],
        [InlineKeyboardButton(text="🏋️ Тренировки", callback_data="programs_soon"), InlineKeyboardButton(text="🍽 Питание / сканер", callback_data="scan_food")],
        [InlineKeyboardButton(text="🧮 Калькуляторы", callback_data="calculators"), InlineKeyboardButton(text="🛠 Управление", callback_data="bot_settings")],
    ])
