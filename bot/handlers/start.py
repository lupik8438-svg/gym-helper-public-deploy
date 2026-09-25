from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.crud import get_user, get_profile, create_user, update_user_activity, create_user_event
from bot.keyboards import get_main_menu
from bot.states import RegistrationStates

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or 'друг'

    # Очищаем состояние и проверяем общую базу пользователей.
    await state.clear()
    user = get_user(user_id)

    if not user:
        # Создаем нового пользователя
        create_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        # Приветственное сообщение для нового пользователя
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

        await message.answer(welcome_text)

        # Запускаем регистрацию
        await start_registration(message, state)

    else:
        # Проверяем наличие профиля
        profile = get_profile(user_id)

        if not profile:
            # Профиль не заполнен - запускаем регистрацию
            await message.answer(
                "👋 С возвращением!\n\n"
                "Вижу, что твой профиль не заполнен. Давай это исправим!"
            )
            await start_registration(message, state)
        else:
            # Все готово - показываем главное меню
            await show_main_menu(message)

    # Пользователь уже гарантированно существует: фиксируем активность безопасно.
    update_user_activity(user_id)
    create_user_event(user_id, "bot_start")

async def start_registration(message: Message, state: FSMContext):
    """Начать процесс регистрации"""
    await state.set_state(RegistrationStates.age)
    await message.answer(
        "Отлично! Ответь на несколько вопросов, чтобы я мог дать тебе персональные рекомендации.\n\n"
        "1️⃣ <b>Сколько тебе лет?</b>\n"
        "Введи свой возраст числом (например: 25)"
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
