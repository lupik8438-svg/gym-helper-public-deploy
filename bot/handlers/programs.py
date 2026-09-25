from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from core.workout_programs import PROGRAM_BY_ID
from database.crud import create_training_session, get_user_dashboard

router = Router()


def _programs_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🏋️ Full Body', callback_data='workout:full_body'), InlineKeyboardButton(text='◈ Сплит', callback_data='workout:split')],
        [InlineKeyboardButton(text='↕ Верх / низ', callback_data='workout:upper_lower'), InlineKeyboardButton(text='↗ Жим · тяни · ноги', callback_data='workout:ppl')],
        [InlineKeyboardButton(text='🚴 Кардио', callback_data='workout:cardio')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')],
    ])


@router.callback_query(F.data == 'programs_soon')
async def show_programs(callback: CallbackQuery):
    await callback.message.edit_text(
        '🏋️ <b>ПЛАНЫ ТРЕНИРОВОК</b>\n\n'
        'Выбери схему — покажу пример тренировочных дней. После занятия можно сохранить запись в прогресс.\n\n'
        'Это общие примеры, а не индивидуальное назначение. Начинай с комфортной нагрузки и следи за техникой.',
        reply_markup=_programs_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith('workout:'))
async def show_program(callback: CallbackQuery):
    program_id = callback.data.split(':', 1)[1]
    program = PROGRAM_BY_ID.get(program_id)
    if not program:
        await callback.answer('План не найден', show_alert=True)
        return
    text = f"🏋️ <b>{program['name']}</b>\n{program['tagline']}\n\n📅 {program['frequency']}\n\n{program['description']}\n\n"
    for day in program['days']:
        text += f"<b>{day['name']} · {day['focus']}</b>\n"
        text += ''.join(f"• {exercise}\n" for exercise in day['exercises']) + '\n'
    if len(text) > 3900:
        text = text[:3800] + '\n\n<i>Список сокращён для отображения в Telegram.</i>'
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Отметить тренировку', callback_data=f'workout_done:{program_id}')],
        [InlineKeyboardButton(text='⬅️ Все программы', callback_data='programs_soon')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')],
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('workout_done:'))
async def log_program_session(callback: CallbackQuery):
    program_id = callback.data.split(':', 1)[1]
    if program_id not in PROGRAM_BY_ID:
        await callback.answer('План не найден', show_alert=True)
        return
    cardio = program_id == 'cardio'
    create_training_session(
        callback.from_user.id,
        program_type=program_id,
        session_type='cardio' if cardio else 'strength',
        duration_minutes=0 if cardio else 45,
        cardio_minutes=30 if cardio else 0,
    )
    dashboard = get_user_dashboard(callback.from_user.id, months=1)
    summary = dashboard['summary']
    await callback.message.edit_text(
        '✅ <b>Тренировка записана</b>\n\n'
        f"🏋️ Всего занятий: <b>{summary['training_sessions']}</b>\n"
        f"🚴 Кардио: <b>{summary['cardio_minutes']} мин</b>\n"
        f"🔥 Активных дней: <b>{summary['active_days']}</b>\n\n"
        'Запись уже учитывается в месячном прогрессе.',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🏋️ Ещё программы', callback_data='programs_soon')],
            [InlineKeyboardButton(text='🗓 Мой прогресс', callback_data='monthly_dashboard')],
            [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')],
        ]),
    )
    await callback.answer('Сохранено')
