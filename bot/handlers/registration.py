from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.crud import create_profile, create_weight_history
from bot.keyboards import (
    get_gender_keyboard,
    get_activity_level_keyboard,
    get_goal_keyboard,
    get_experience_keyboard,
    get_cancel_registration_keyboard,
    get_main_menu
)
from bot.states import RegistrationStates
from utils.helpers import validate_age, validate_height, validate_weight, validate_target_weight, validate_range

router = Router()

# ===== ВОЗРАСТ =====
@router.message(RegistrationStates.age)
async def process_age(message: Message, state: FSMContext):
    """Обработка ввода возраста"""
    is_valid, age, error = validate_age(message.text)

    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуй еще раз:")
        return

    await state.update_data(age=age)
    await state.set_state(RegistrationStates.gender)

    await message.answer(
        f"Отлично! Тебе {age} лет.\n\n"
        "2️⃣ <b>Укажи свой пол:</b>",
        reply_markup=get_gender_keyboard()
    )

# ===== ПОЛ =====
@router.callback_query(RegistrationStates.gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора пола"""
    gender = callback.data.split("_")[1]  # male или female
    await state.update_data(gender=gender)
    await state.set_state(RegistrationStates.height)

    gender_text = "мужской" if gender == "male" else "женский"

    await callback.message.edit_text(
        f"Пол: {gender_text} ✅\n\n"
        "3️⃣ <b>Какой у тебя рост?</b>\n"
        "Введи рост в сантиметрах (например: 175)"
    , reply_markup=get_cancel_registration_keyboard())
    await callback.answer()

# ===== РОСТ =====
@router.message(RegistrationStates.height)
async def process_height(message: Message, state: FSMContext):
    """Обработка ввода роста"""
    is_valid, height, error = validate_height(message.text)

    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуй еще раз:")
        return

    await state.update_data(height=height)
    await state.set_state(RegistrationStates.current_weight)

    await message.answer(
        f"Рост: {height} см ✅\n\n"
        "4️⃣ <b>Сколько ты сейчас весишь?</b>\n"
        "Введи текущий вес в килограммах (например: 75 или 75.5)"
    , reply_markup=get_cancel_registration_keyboard())

# ===== ТЕКУЩИЙ ВЕС =====
@router.message(RegistrationStates.current_weight)
async def process_current_weight(message: Message, state: FSMContext):
    """Обработка ввода текущего веса"""
    is_valid, weight, error = validate_weight(message.text)

    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуй еще раз:")
        return

    await state.update_data(current_weight=weight)
    await state.set_state(RegistrationStates.target_weight)

    await message.answer(
        f"Текущий вес: {weight} кг ✅\n\n"
        "5️⃣ <b>Какой вес ты хочешь достичь?</b>\n"
        "Введи целевой вес в килограммах (например: 70)"
    )

# ===== ЦЕЛЕВОЙ ВЕС =====
@router.message(RegistrationStates.target_weight)
async def process_target_weight(message: Message, state: FSMContext):
    """Обработка ввода целевого веса"""
    data = await state.get_data()
    current_weight = data['current_weight']

    is_valid, target_weight, error = validate_target_weight(current_weight, message.text)

    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуй еще раз:")
        return

    await state.update_data(target_weight=target_weight)
    await state.set_state(RegistrationStates.activity_level)

    # Рассчитываем разницу
    diff = target_weight - current_weight
    if diff > 0:
        change_text = f"Планируешь набрать {diff:.1f} кг 📈"
    elif diff < 0:
        change_text = f"Планируешь сбросить {abs(diff):.1f} кг 📉"
    else:
        change_text = "Хочешь поддерживать текущий вес ⚖️"

    await message.answer(
        f"Целевой вес: {target_weight} кг ✅\n"
        f"{change_text}\n\n"
        "6️⃣ <b>Какой у тебя уровень физической активности?</b>",
        reply_markup=get_activity_level_keyboard()
    )

# ===== УРОВЕНЬ АКТИВНОСТИ =====
@router.callback_query(RegistrationStates.activity_level, F.data.startswith("activity_"))
async def process_activity_level(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора уровня активности"""
    activity = callback.data.removeprefix("activity_")
    await state.update_data(activity_level=activity)
    await state.set_state(RegistrationStates.goal)

    activity_labels = {
        'sedentary': 'Сидячий образ жизни',
        'light': 'Легкая активность',
        'moderate': 'Умеренная активность',
        'active': 'Высокая активность',
        'very_active': 'Очень высокая активность'
    }

    await callback.message.edit_text(
        f"Уровень активности: {activity_labels[activity]} ✅\n\n"
        "7️⃣ <b>Какая у тебя основная цель?</b>",
        reply_markup=get_goal_keyboard()
    )
    await callback.answer()

# ===== ЦЕЛЬ =====
@router.callback_query(RegistrationStates.goal, F.data.startswith("goal_"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора цели"""
    goal = callback.data.split("_", 1)[1]  # lose_weight, maintain, gain_muscle
    await state.update_data(goal=goal)
    await state.set_state(RegistrationStates.experience_level)

    goal_labels = {
        'lose_weight': 'Похудение',
        'maintain': 'Поддержание веса',
        'gain_muscle': 'Набор мышечной массы'
    }

    await callback.message.edit_text(
        f"Цель: {goal_labels[goal]} ✅\n\n"
        "8️⃣ <b>И последний вопрос - какой у тебя опыт тренировок?</b>",
        reply_markup=get_experience_keyboard()
    )
    await callback.answer()

# ===== ОПЫТ И ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ =====
@router.callback_query(RegistrationStates.experience_level, F.data.startswith("exp_"))
async def process_experience(callback: CallbackQuery, state: FSMContext):
    """После базовых данных собираем режим тренировок и сон."""
    experience = callback.data.split("_")[1]
    await state.update_data(experience_level=experience)
    await state.set_state(RegistrationStates.training_days)
    await callback.message.edit_text(
        "Опыт тренировок сохранён ✅\n\n"
        "9️⃣ <b>Сколько тренировок в неделю ты реально планируешь?</b>\n"
        "Введи число от 0 до 7 (например: 3)"
    , reply_markup=get_cancel_registration_keyboard())
    await callback.answer()


@router.message(RegistrationStates.training_days)
async def process_training_days(message: Message, state: FSMContext):
    is_valid, value, error = validate_range(message.text, 0, 7, "Количество тренировок", integer=True)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуй ещё раз:")
        return
    await state.update_data(training_days_per_week=value)
    await state.set_state(RegistrationStates.sleep_hours)
    await message.answer(
        f"Тренировок в неделю: {value} ✅\n\n"
        "🔟 <b>Сколько часов ты обычно спишь?</b>\n"
        "Введи число от 3 до 14 (например: 8)"
    , reply_markup=get_cancel_registration_keyboard())


@router.message(RegistrationStates.sleep_hours)
async def process_sleep_hours(message: Message, state: FSMContext):
    is_valid, value, error = validate_range(message.text, 3, 14, "Количество часов сна")
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуй ещё раз:")
        return
    await state.update_data(sleep_hours=value)
    data = await state.get_data()
    user_id = message.from_user.id
    create_profile(
        user_id=user_id, age=data['age'], gender=data['gender'], height=data['height'],
        current_weight=data['current_weight'], target_weight=data['target_weight'],
        activity_level=data['activity_level'], goal=data['goal'],
        experience_level=data['experience_level'],
        training_days_per_week=data['training_days_per_week'], sleep_hours=value,
    )
    create_weight_history(user_id, data['current_weight'])
    await state.clear()
    exp_labels = {'beginner': 'Новичок', 'intermediate': 'Средний уровень', 'advanced': 'Продвинутый'}
    completion_text = (
        "╭──────────────────╮\n"
        "│  🎉 <b>ПРОФИЛЬ ГОТОВ</b>  │\n"
        "╰──────────────────╯\n\n"
        "Теперь бот, Mini App и сайт будут видеть одни и те же данные.\n\n"
        f"📊 <b>{data['current_weight']} кг</b> → <b>{data['target_weight']} кг</b>\n"
        f"🏋️ Тренировки: <b>{data['training_days_per_week']}/нед.</b> · 😴 Сон: <b>{value:.1f} ч</b>\n"
        f"🏆 Опыт: <b>{exp_labels[data['experience_level']]}</b>\n\n"
        "Первые достижения появятся, когда начнёшь отмечать вес и питание."
    )
    await message.answer(completion_text, reply_markup=get_main_menu())

