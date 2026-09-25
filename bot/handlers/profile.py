from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from datetime import datetime

from database.crud import get_user, get_profile, update_profile, get_weight_history, create_weight_history, get_user_dashboard, create_user_event
from bot.keyboards import (
    get_profile_menu,
    get_edit_profile_menu,
    get_gender_keyboard,
    get_activity_level_keyboard,
    get_goal_keyboard,
    get_experience_keyboard,
    get_main_menu,
    get_profile_input_keyboard
)
from bot.states import ProfileEditStates
from utils.formatters import format_profile, format_weight_history
from utils.helpers import (
    validate_age,
    validate_height,
    validate_weight,
    validate_target_weight
)

router = Router()

@router.callback_query(F.data == "my_profile")
async def show_profile(callback: CallbackQuery):
    """Показать профиль пользователя"""
    user_id = callback.from_user.id
    user = get_user(user_id)
    profile = get_profile(user_id)

    if not profile:
        await callback.answer(
            "❌ Профиль не найден. Создай его через /start",
            show_alert=True
        )
        return

    # Форматируем данные пользователя
    user_info = {
        'first_name': user.first_name,
        'username': user.username,
        'created_at': user.created_at.strftime('%d.%m.%Y') if user.created_at else 'недавно'
    }

    # Форматируем данные профиля
    profile_data = {
        'age': profile.age,
        'gender': profile.gender,
        'height': profile.height,
        'current_weight': profile.current_weight,
        'target_weight': profile.target_weight,
        'activity_level': profile.activity_level,
        'goal': profile.goal,
        'experience_level': profile.experience_level,
        'training_days_per_week': profile.training_days_per_week,
        'sleep_hours': profile.sleep_hours
    }

    message = format_profile(profile_data, user_info)

    await callback.message.edit_text(
        message,
        reply_markup=get_profile_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "edit_profile")
async def show_edit_menu(callback: CallbackQuery):
    """Показать меню редактирования"""
    await callback.message.edit_text(
        "✏️ <b>Редактирование профиля</b>\n\n"
        "Что хочешь изменить?",
        reply_markup=get_edit_profile_menu()
    )
    await callback.answer()

# ===== РЕДАКТИРОВАНИЕ ВОЗРАСТА =====
@router.callback_query(F.data == "edit_age")
async def edit_age_start(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование возраста"""
    await state.set_state(ProfileEditStates.edit_age)
    await callback.message.edit_text(
        "🎂 <b>Изменение возраста</b>\n\n"
        "Введи свой возраст числом (например: 25)"
    , reply_markup=get_profile_input_keyboard())
    await callback.answer()

@router.message(ProfileEditStates.edit_age)
async def edit_age_process(message: Message, state: FSMContext):
    """Обработка нового возраста"""
    is_valid, age, error = validate_age(message.text)

    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуй еще раз:")
        return

    user_id = message.from_user.id
    update_profile(user_id, age=age)

    await state.clear()
    await message.answer(
        f"✅ Возраст обновлен: {age} лет",
        reply_markup=get_profile_menu()
    )

# ===== РЕДАКТИРОВАНИЕ ПОЛА =====
@router.callback_query(F.data == "edit_gender")
async def edit_gender_start(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование пола"""
    await state.set_state(ProfileEditStates.edit_gender)
    await callback.message.edit_text(
        "⚧️ <b>Изменение пола</b>\n\n"
        "Укажи свой пол:",
        reply_markup=get_gender_keyboard()
    )
    await callback.answer()

@router.callback_query(ProfileEditStates.edit_gender, F.data.startswith("gender_"))
async def edit_gender_process(callback: CallbackQuery, state: FSMContext):
    """Обработка нового пола"""
    gender = callback.data.split("_")[1]
    user_id = callback.from_user.id
    update_profile(user_id, gender=gender)

    await state.clear()

    gender_text = "мужской" if gender == "male" else "женский"
    await callback.message.edit_text(
        f"✅ Пол обновлен: {gender_text}",
        reply_markup=get_profile_menu()
    )
    await callback.answer()

# ===== РЕДАКТИРОВАНИЕ РОСТА =====
@router.callback_query(F.data == "edit_height")
async def edit_height_start(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование роста"""
    await state.set_state(ProfileEditStates.edit_height)
    await callback.message.edit_text(
        "📏 <b>Изменение роста</b>\n\n"
        "Введи рост в сантиметрах (например: 175)"
    , reply_markup=get_profile_input_keyboard())
    await callback.answer()

@router.message(ProfileEditStates.edit_height)
async def edit_height_process(message: Message, state: FSMContext):
    """Обработка нового роста"""
    is_valid, height, error = validate_height(message.text)

    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуй еще раз:")
        return

    user_id = message.from_user.id
    update_profile(user_id, height=height)

    await state.clear()
    await message.answer(
        f"✅ Рост обновлен: {height} см",
        reply_markup=get_profile_menu()
    )

# ===== РЕДАКТИРОВАНИЕ ТЕКУЩЕГО ВЕСА =====
@router.callback_query(F.data == "edit_current_weight")
async def edit_current_weight_start(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование текущего веса"""
    await state.set_state(ProfileEditStates.edit_current_weight)
    await callback.message.edit_text(
        "⚖️ <b>Изменение текущего веса</b>\n\n"
        "Введи вес в килограммах (например: 75 или 75.5)"
    , reply_markup=get_profile_input_keyboard())
    await callback.answer()

@router.message(ProfileEditStates.edit_current_weight)
async def edit_current_weight_process(message: Message, state: FSMContext):
    """Обработка нового веса"""
    is_valid, weight, error = validate_weight(message.text)

    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуй еще раз:")
        return

    user_id = message.from_user.id
    update_profile(user_id, current_weight=weight)

    # Добавляем запись в историю веса
    create_weight_history(user_id, weight)

    await state.clear()
    await message.answer(
        f"✅ Вес обновлен: {weight} кг\n"
        f"📝 Добавлена запись в историю веса",
        reply_markup=get_profile_menu()
    )

# ===== РЕДАКТИРОВАНИЕ ЦЕЛЕВОГО ВЕСА =====
@router.callback_query(F.data == "edit_target_weight")
async def edit_target_weight_start(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование целевого веса"""
    await state.set_state(ProfileEditStates.edit_target_weight)
    await callback.message.edit_text(
        "🎯 <b>Изменение целевого веса</b>\n\n"
        "Введи целевой вес в килограммах (например: 70)"
    , reply_markup=get_profile_input_keyboard())
    await callback.answer()

@router.message(ProfileEditStates.edit_target_weight)
async def edit_target_weight_process(message: Message, state: FSMContext):
    """Обработка нового целевого веса"""
    user_id = message.from_user.id
    profile = get_profile(user_id)

    is_valid, target_weight, error = validate_target_weight(profile.current_weight, message.text)

    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуй еще раз:")
        return

    update_profile(user_id, target_weight=target_weight)

    await state.clear()
    await message.answer(
        f"✅ Целевой вес обновлен: {target_weight} кг",
        reply_markup=get_profile_menu()
    )

# ===== РЕДАКТИРОВАНИЕ УРОВНЯ АКТИВНОСТИ =====
@router.callback_query(F.data == "edit_activity")
async def edit_activity_start(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование уровня активности"""
    await state.set_state(ProfileEditStates.edit_activity_level)
    await callback.message.edit_text(
        "🏃 <b>Изменение уровня активности</b>\n\n"
        "Какой у тебя уровень физической активности?",
        reply_markup=get_activity_level_keyboard()
    )
    await callback.answer()

@router.callback_query(ProfileEditStates.edit_activity_level, F.data.startswith("activity_"))
async def edit_activity_process(callback: CallbackQuery, state: FSMContext):
    """Обработка нового уровня активности"""
    activity = callback.data.removeprefix("activity_")
    user_id = callback.from_user.id
    update_profile(user_id, activity_level=activity)

    await state.clear()

    activity_labels = {
        'sedentary': 'Сидячий образ жизни',
        'light': 'Легкая активность',
        'moderate': 'Умеренная активность',
        'active': 'Высокая активность',
        'very_active': 'Очень высокая активность'
    }

    await callback.message.edit_text(
        f"✅ Уровень активности обновлен: {activity_labels[activity]}",
        reply_markup=get_profile_menu()
    )
    await callback.answer()

# ===== РЕДАКТИРОВАНИЕ ЦЕЛИ =====
@router.callback_query(F.data == "edit_goal")
async def edit_goal_start(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование цели"""
    await state.set_state(ProfileEditStates.edit_goal)
    await callback.message.edit_text(
        "🎯 <b>Изменение цели</b>\n\n"
        "Какая у тебя основная цель?",
        reply_markup=get_goal_keyboard()
    )
    await callback.answer()

@router.callback_query(ProfileEditStates.edit_goal, F.data.startswith("goal_"))
async def edit_goal_process(callback: CallbackQuery, state: FSMContext):
    """Обработка новой цели"""
    goal = callback.data.split("_", 1)[1]
    user_id = callback.from_user.id
    update_profile(user_id, goal=goal)

    await state.clear()

    goal_labels = {
        'lose_weight': 'Похудение',
        'maintain': 'Поддержание веса',
        'gain_muscle': 'Набор мышечной массы'
    }

    await callback.message.edit_text(
        f"✅ Цель обновлена: {goal_labels[goal]}",
        reply_markup=get_profile_menu()
    )
    await callback.answer()

# ===== РЕДАКТИРОВАНИЕ ОПЫТА =====
@router.callback_query(F.data == "edit_experience")
async def edit_experience_start(callback: CallbackQuery, state: FSMContext):
    """Начать редактирование опыта"""
    await state.set_state(ProfileEditStates.edit_experience_level)
    await callback.message.edit_text(
        "💪 <b>Изменение уровня опыта</b>\n\n"
        "Какой у тебя опыт тренировок?",
        reply_markup=get_experience_keyboard()
    )
    await callback.answer()

@router.callback_query(ProfileEditStates.edit_experience_level, F.data.startswith("exp_"))
async def edit_experience_process(callback: CallbackQuery, state: FSMContext):
    """Обработка нового опыта"""
    experience = callback.data.split("_")[1]
    user_id = callback.from_user.id
    update_profile(user_id, experience_level=experience)

    await state.clear()

    exp_labels = {
        'beginner': 'Новичок',
        'intermediate': 'Средний уровень',
        'advanced': 'Продвинутый'
    }

    await callback.message.edit_text(
        f"✅ Опыт обновлен: {exp_labels[experience]}",
        reply_markup=get_profile_menu()
    )
    await callback.answer()


# ===== ДОПОЛНИТЕЛЬНЫЕ ПОЛЯ ПРОФИЛЯ =====
@router.callback_query(F.data == "edit_training_days")
async def edit_training_days_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileEditStates.edit_training_days)
    await callback.message.edit_text("🏋️ <b>Тренировки в неделю</b>\n\nВведи число от 0 до 7:", reply_markup=get_profile_input_keyboard())
    await callback.answer()


@router.message(ProfileEditStates.edit_training_days)
async def edit_training_days_process(message: Message, state: FSMContext):
    try:
        value = int(message.text)
    except (TypeError, ValueError):
        await message.answer("❌ Введи целое число от 0 до 7:")
        return
    if value < 0 or value > 7:
        await message.answer("❌ Введи число от 0 до 7:")
        return
    update_profile(message.from_user.id, training_days_per_week=value)
    create_user_event(message.from_user.id, 'profile_updated', {'field': 'training_days_per_week', 'value': value})
    await state.clear()
    await message.answer(f"✅ План тренировок обновлён: {value} / нед.", reply_markup=get_profile_menu())


@router.callback_query(F.data == "edit_sleep_hours")
async def edit_sleep_hours_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileEditStates.edit_sleep_hours)
    await callback.message.edit_text("😴 <b>Сон</b>\n\nСколько часов ты обычно спишь? Введи число от 3 до 14:", reply_markup=get_profile_input_keyboard())
    await callback.answer()


@router.message(ProfileEditStates.edit_sleep_hours)
async def edit_sleep_hours_process(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(',', '.'))
    except (TypeError, ValueError):
        await message.answer("❌ Введи число от 3 до 14:")
        return
    if value < 3 or value > 14:
        await message.answer("❌ Введи число от 3 до 14:")
        return
    update_profile(message.from_user.id, sleep_hours=value)
    create_user_event(message.from_user.id, 'profile_updated', {'field': 'sleep_hours', 'value': value})
    await state.clear()
    await message.answer(f"✅ Сон обновлён: {value:g} ч", reply_markup=get_profile_menu())


@router.callback_query(F.data == "monthly_dashboard")
async def show_monthly_dashboard(callback: CallbackQuery):
    dashboard = get_user_dashboard(callback.from_user.id, months=6)
    summary = dashboard['summary']
    monthly = dashboard['monthly']
    current = monthly[-1] if monthly else {}
    achievements = dashboard['achievements']
    achievement_text = '\n'.join(
        f"{'✅' if item['done'] else '⬜️'} {item['icon']} {item['title']}"
        for item in achievements
    )
    message = (
        "╭────────────────────╮\n"
        "│  🗓 <b>МОЙ ПРОГРЕСС</b>  │\n"
        "╰────────────────────╯\n\n"
        f"🔥 Серия активности: <b>{summary['streak_days']} дн.</b>\n"
        f"🎯 Путь к цели: <b>{summary['goal_progress'] or 0}%</b>\n"
        f"⚖️ Замеров веса: <b>{summary['weight_entries']}</b>\n"
        f"🍽 Записей питания: <b>{summary['food_entries']}</b>\n\n"
        "<b>Текущий месяц</b>\n"
        f"• Активных дней: <b>{current.get('active_days', 0)}</b>\n"
        f"• Изменение веса: <b>{current.get('weight_change', 0):+.1f} кг</b>\n"
        f"• Калории: <b>{current.get('calories', 0)}</b>\n\n"
        "<b>Достижения</b>\n" + achievement_text
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 История веса", callback_data="weight_history")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="my_profile"), InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")]
    ])
    await callback.message.edit_text(message, reply_markup=keyboard)
    await callback.answer()

# ===== ИСТОРИЯ ВЕСА =====
@router.callback_query(F.data == "weight_history")
async def show_weight_history(callback: CallbackQuery):
    """Показать историю веса"""
    user_id = callback.from_user.id
    history = get_weight_history(user_id)

    # Преобразуем в словари для форматирования
    history_data = [
        {
            'weight': record.weight,
            'recorded_at': record.recorded_at
        }
        for record in history
    ]

    message = format_weight_history(history_data)

    # Кнопка возврата
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад к профилю", callback_data="my_profile")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(message, reply_markup=keyboard)
    await callback.answer()

# ===== ОБНОВИТЬ ВЕС =====
@router.callback_query(F.data == "update_weight")
async def update_weight_start(callback: CallbackQuery, state: FSMContext):
    """Быстрое обновление веса"""
    await state.set_state(ProfileEditStates.edit_current_weight)
    await callback.message.edit_text(
        "⚖️ <b>Обновить вес</b>\n\n"
        "Введи свой текущий вес в килограммах:"
    , reply_markup=get_profile_input_keyboard())
    await callback.answer()
