"""Phone opt-in, settings and user-data controls."""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardRemove

from bot.keyboards import get_main_menu, get_management_menu, get_phone_request_keyboard
from database.connection import SessionLocal
from database.models import User
from database.crud import create_user_event, get_user
from bot.states import RegistrationStates

router = Router()


@router.callback_query(F.data == 'bot_settings')
async def settings_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    await callback.message.edit_text(
        '🛠 <b>Управление аккаунтом</b>\n\n'
        'Здесь можно настроить контакт для будущих напоминаний и посмотреть управление данными. '
        'Телефон необязателен и используется только после явного согласия.',
        reply_markup=get_management_menu(bool(user and user.phone_number)),
    )
    await callback.answer()


@router.callback_query(F.data == 'phone_share_info')
async def phone_info(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationStates.phone)
    await state.update_data(after_phone='menu')
    await callback.message.answer(
        '📱 Номер телефона — по желанию. Telegram покажет системную кнопку отправки контакта; '
        'мы принимаем только номер, которым владеет текущий аккаунт Telegram. '
        'Не отправляй номер обычным текстом.',
        reply_markup=get_phone_request_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == 'my_data')
async def show_my_data(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    text = '🗂 <b>Твои данные</b>\n\n'
    if user and user.phone_number:
        text += '📱 Телефон привязан. '
        text += 'Можешь удалить его кнопкой ниже.\n\n'
    else:
        text += 'Телефон не привязан. Профиль и прогресс хранятся без номера.\n\n'
    text += 'Профиль, вес, питание и тренировки используются для твоей статистики в Gym Helper.'
    rows = []
    if user and user.phone_number:
        rows.append([InlineKeyboardButton(text='🗑 Удалить телефон', callback_data='phone_delete')])
    rows.append([InlineKeyboardButton(text='⬅️ Управление', callback_data='bot_settings')])
    rows.append([InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')])
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data == 'phone_delete')
async def delete_phone(callback: CallbackQuery):
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(user_id=callback.from_user.id).first()
        if user:
            user.phone_number = None
            db.commit()
    finally:
        db.close()
    create_user_event(callback.from_user.id, 'phone_deleted')
    await callback.message.edit_text('✅ Номер удалён из профиля.', reply_markup=get_management_menu(False))
    await callback.answer()


@router.callback_query(F.data == 'reminders_info')
async def reminders_info(callback: CallbackQuery):
    await callback.answer('Напоминания ещё не включены. Сначала добавим расписание и согласие на уведомления.', show_alert=True)
