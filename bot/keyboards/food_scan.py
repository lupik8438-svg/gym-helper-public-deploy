from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_food_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Сохранить', callback_data='food_confirm'), InlineKeyboardButton(text='✏️ Изменить', callback_data='food_adjust')],
        [InlineKeyboardButton(text='🔄 Заново', callback_data='food_rescan'), InlineKeyboardButton(text='❌ Отмена', callback_data='food_cancel')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')],
    ])


def get_daily_stats_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📊 Статистика', callback_data='daily_stats'), InlineKeyboardButton(text='📸 Ещё фото', callback_data='scan_food')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')],
    ])
