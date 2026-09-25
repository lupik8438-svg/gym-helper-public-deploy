"""Глобальные команды управления состоянием бота."""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.keyboards import get_main_menu
from database.crud import get_profile, create_user_event

router = Router()


def _home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')],
    ])


def _menu_text() -> str:
    return (
        '╭──────────────────╮\n'
        '│  🏠 <b>GYM HELPER</b>  │\n'
        '╰──────────────────╯\n\n'
        'Выбери действие — я помогу превратить данные в следующий шаг.'
    )


@router.message(Command('cancel'))
async def cancel_command(message: Message, state: FSMContext):
    """Отменяет любое активное FSM-состояние, независимо от текущего раздела."""
    current_state = await state.get_state()
    await state.clear()
    create_user_event(message.from_user.id, 'action_cancelled', {'state': current_state})

    if current_state:
        await message.answer(
            '✅ Действие отменено.\n\nВозвращаемся в главное меню:',
            reply_markup=get_main_menu(),
        )
    else:
        await message.answer(_menu_text(), reply_markup=get_main_menu())


@router.message(Command('menu'))
async def menu_command(message: Message, state: FSMContext):
    """Короткая команда возврата в меню для мобильного Telegram."""
    await state.clear()
    await message.answer(_menu_text(), reply_markup=get_main_menu())


@router.callback_query(F.data.in_({'cancel_action', 'cancel_registration'}))
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    create_user_event(callback.from_user.id, 'action_cancelled', {'source': 'button'})
    await callback.message.edit_text(
        '✅ Действие отменено.\n\nВозвращаемся в главное меню:',
        reply_markup=get_main_menu(),
    )
    await callback.answer('Отменено')


@router.callback_query(F.data == 'quick_main_menu')
async def quick_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(_menu_text(), reply_markup=get_main_menu())
    await callback.answer()
