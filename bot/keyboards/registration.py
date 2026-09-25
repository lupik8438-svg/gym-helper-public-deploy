from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def _cancel_row():
    return [InlineKeyboardButton(text='❌ Отмена регистрации', callback_data='cancel_registration')]


def get_cancel_registration_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[_cancel_row()])


def get_gender_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='👨 Мужской', callback_data='gender_male'), InlineKeyboardButton(text='👩 Женский', callback_data='gender_female')],
        _cancel_row(),
    ])


def get_activity_level_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🛋 Сидячий', callback_data='activity_sedentary'), InlineKeyboardButton(text='🚶 Лёгкая', callback_data='activity_light')],
        [InlineKeyboardButton(text='🏃 Умеренная', callback_data='activity_moderate'), InlineKeyboardButton(text='🏋️ Высокая', callback_data='activity_active')],
        [InlineKeyboardButton(text='💪 Очень высокая', callback_data='activity_very_active')],
        _cancel_row(),
    ])


def get_goal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📉 Похудение', callback_data='goal_lose_weight'), InlineKeyboardButton(text='⚖️ Поддержание', callback_data='goal_maintain')],
        [InlineKeyboardButton(text='📈 Набор массы', callback_data='goal_gain_muscle')],
        _cancel_row(),
    ])


def get_experience_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🌱 Новичок', callback_data='exp_beginner'), InlineKeyboardButton(text='💪 Средний', callback_data='exp_intermediate')],
        [InlineKeyboardButton(text='🏆 Продвинутый', callback_data='exp_advanced')],
        _cancel_row(),
    ])
