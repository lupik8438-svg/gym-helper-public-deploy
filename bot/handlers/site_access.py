"""One-time website access code issued by Telegram."""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import PUBLIC_SITE_URL
from bot.keyboards import get_main_menu, get_management_menu, get_phone_request_keyboard
from database.crud import create_site_access_code, get_user
from bot.states import RegistrationStates

router = Router()


async def _issue_code(message: Message):
    user = get_user(message.from_user.id)
    if not user or not user.phone_number:
        await message.answer(
            'Сначала привяжи номер в разделе управления. Это нужно, чтобы вход на сайт был только твоим.',
            reply_markup=get_phone_request_keyboard(),
        )
        return
    code, expires_at = create_site_access_code(message.from_user.id, user.phone_number)
    site = PUBLIC_SITE_URL.rstrip('/') if PUBLIC_SITE_URL else 'адрес сайта появится после публикации'
    await message.answer(
        '🌐 <b>Вход на сайт Gym Helper</b>\n\n'
        f'Адрес: <code>{site}</code>\n'
        f'Телефон: <code>+{user.phone_number}</code>\n'
        f'Одноразовый код: <code>{code}</code>\n\n'
        'Код действует 10 минут и используется один раз. Никому его не пересылай.',
        reply_markup=get_management_menu(True),
    )


@router.message(Command('site'))
async def site_command(message: Message, state: FSMContext):
    await state.clear()
    await _issue_code(message)


@router.callback_query(F.data == 'site_access')
async def site_access_callback(callback: CallbackQuery):
    await _issue_code(callback.message)
    await callback.answer('Код отправлен')
