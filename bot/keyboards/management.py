from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup


def get_management_menu(phone_shared: bool = False) -> InlineKeyboardMarkup:
    phone_label = '✅ Телефон привязан' if phone_shared else '📱 Добавить телефон'
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=phone_label, callback_data='phone_share_info' if phone_shared else 'phone_share_info')],
        [InlineKeyboardButton(text='👤 Профиль', callback_data='my_profile'), InlineKeyboardButton(text='📈 Прогресс', callback_data='monthly_dashboard')],
        [InlineKeyboardButton(text='🔔 Напоминания', callback_data='reminders_info'), InlineKeyboardButton(text='🗂 Мои данные', callback_data='my_data')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')],
    ])


def get_phone_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='📱 Поделиться номером', request_contact=True)], [KeyboardButton(text='Отмена')]],
        resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Нажми, чтобы отправить свой номер',
    )
