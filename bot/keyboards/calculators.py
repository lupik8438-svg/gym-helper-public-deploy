from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_calculators_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📏 ИМТ / BMI', callback_data='calc_bmi'), InlineKeyboardButton(text='🔥 Калории', callback_data='calc_calories')],
        [InlineKeyboardButton(text='💊 Добавки', callback_data='calc_supplements')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu'), InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_action')],
    ])


def get_back_to_calculators() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⬅️ К калькуляторам', callback_data='calculators')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')],
    ])
