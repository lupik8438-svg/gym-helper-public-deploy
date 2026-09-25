from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_profile_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✏️ Редактировать профиль', callback_data='edit_profile')],
        [InlineKeyboardButton(text='⚖️ Обновить вес', callback_data='update_weight'), InlineKeyboardButton(text='📈 История', callback_data='weight_history')],
        [InlineKeyboardButton(text='🗓 Месячный прогресс', callback_data='monthly_dashboard')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')],
    ])


def get_edit_profile_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🎂 Возраст', callback_data='edit_age'), InlineKeyboardButton(text='📏 Рост', callback_data='edit_height')],
        [InlineKeyboardButton(text='⚖️ Текущий вес', callback_data='edit_current_weight'), InlineKeyboardButton(text='🎯 Целевой вес', callback_data='edit_target_weight')],
        [InlineKeyboardButton(text='🏃 Активность', callback_data='edit_activity'), InlineKeyboardButton(text='🎯 Цель', callback_data='edit_goal')],
        [InlineKeyboardButton(text='💪 Опыт', callback_data='edit_experience'), InlineKeyboardButton(text='🏋️ Тренировки', callback_data='edit_training_days')],
        [InlineKeyboardButton(text='😴 Сон', callback_data='edit_sleep_hours')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')],
    ])


def get_profile_input_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⬅️ К профилю', callback_data='my_profile'), InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')],
        [InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_action')],
    ])
