from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from database.crud import get_user, get_profile, create_user, update_user_activity, create_user_event
from bot.keyboards import get_main_menu, get_phone_request_keyboard
from bot.states import RegistrationStates
from pathlib import Path

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Open the bot with a visual welcome and a mobile-first next action."""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or 'друг'
    await state.clear()
    user = get_user(user_id)
    hero = Path(__file__).resolve().parents[2] / 'website' / 'static' / 'images' / 'fitness-hero.jpg'

    welcome_text = (
        f"╭──────────────────╮\n"
        f"│  👋 <b>ПРИВЕТ, {first_name.upper()}!</b>  │\n"
        f"╰──────────────────╯\n\n"
        "Добро пожаловать в <b>Gym Helper</b> — спокойный фитнес-помощник для ежедневного прогресса. 💪\n\n"
        "<b>Что будет внутри:</b>\n"
        "📊 расчёт калорий и макронутриентов\n"
        "📸 анализ еды по фото\n"
        "💊 рекомендации по добавкам\n"
        "📈 история веса и понятная динамика\n\n"
        "Давай начнём с короткого профиля — это займёт пару минут."
    )
    try:
        if hero.exists():
            await message.answer_photo(FSInputFile(hero), caption=welcome_text if not user else f'👋 С возвращением, <b>{first_name}</b>!')
        elif not user:
            await message.answer(welcome_text)
    except Exception:
        # The image is decorative; a broken Telegram media upload must not block the bot.
        if not user:
            await message.answer(welcome_text)

    if not user:
        create_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        await start_registration(message, state)
    else:
        profile = get_profile(user_id)
        if not profile:
            await message.answer(
                "👋 С возвращением!\n\n"
                "Вижу, что твой профиль не заполнен. Давай это исправим!"
            )
            await start_registration(message, state)
        elif not user.phone_number:
            await state.set_state(RegistrationStates.phone)
            await state.update_data(after_phone='menu')
            await message.answer(
                "👋 Профиль уже готов. Если хочешь, привяжи номер для будущих напоминаний — это необязательно.",
                reply_markup=get_phone_request_keyboard(),
            )
        else:
            await show_main_menu(message)

    update_user_activity(user_id)
    create_user_event(user_id, "bot_start")

async def start_registration(message: Message, state: FSMContext):
    """Начать регистрацию с опционального подтверждения номера телефона."""
    await state.set_state(RegistrationStates.phone)
    await state.update_data(after_phone='profile')
    await message.answer(
        "📱 <b>Шаг 0 из 10 · контакт</b>\n\n"
        "Номер телефона необязателен. Если поделишься им через системную кнопку Telegram, "
        "мы сможем добавить напоминания и восстановление доступа в будущем. Обычным текстом номер не отправляй.",
        reply_markup=get_phone_request_keyboard(),
    )

async def show_main_menu(message: Message):
    """Показать главное меню"""
    menu_text = (
        "╭──────────────────╮\n"
        "│  🏠 <b>GYM HELPER</b>  │\n"
        "╰──────────────────╯\n\n"
        "Выбери действие — я помогу превратить данные в следующий шаг."
    )
    await message.answer(menu_text, reply_markup=get_main_menu())

@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню через callback"""
    await state.clear()

    menu_text = (
        "╭──────────────────╮\n"
        "│  🏠 <b>GYM HELPER</b>  │\n"
        "╰──────────────────╯\n\n"
        "Выбери действие — я помогу превратить данные в следующий шаг."
    )

    await callback.message.edit_text(menu_text, reply_markup=get_main_menu())
    await callback.answer()

@router.callback_query(F.data == "app_setup")
async def callback_app_setup(callback: CallbackQuery):
    await callback.answer(
        "Mini App пока не подключен: владельцу нужно указать публичный HTTPS-адрес в WEBAPP_PUBLIC_URL и перезапустить бота.",
        show_alert=True
    )

@router.callback_query(F.data == "exercises_soon")
async def callback_coming_soon(callback: CallbackQuery):
    """Функции в разработке"""
    feature_names = {
        "exercises_soon": "База упражнений",
    }

    feature = feature_names.get(callback.data, "Эта функция")

    await callback.answer(
        f"🚧 {feature} скоро появится!\n"
        "Следи за обновлениями.",
        show_alert=True
    )
