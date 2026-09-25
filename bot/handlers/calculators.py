from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.crud import get_profile, create_user_event
from core.calculators.bmi import calculate_bmi
from core.calculators.calories import calculate_full_nutrition
from core.calculators.supplements import calculate_supplement_recommendations
from bot.keyboards import get_calculators_menu, get_back_to_calculators
from utils.formatters import format_bmi_result, format_calories_result, format_supplements_result

router = Router()

@router.callback_query(F.data == "calculators")
async def show_calculators_menu(callback: CallbackQuery):
    """Показать меню калькуляторов"""
    await callback.message.edit_text(
        "╭──────────────────╮\n"
        "│  📊 <b>РАСЧЁТЫ</b>  │\n"
        "╰──────────────────╯\n\n"
        "Выбери показатель — я соберу персональный ориентир:",
        reply_markup=get_calculators_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "calc_bmi")
async def calculate_bmi_handler(callback: CallbackQuery):
    """Рассчитать BMI"""
    user_id = callback.from_user.id
    profile = get_profile(user_id)

    if not profile:
        await callback.answer(
            "❌ Сначала создай профиль через /start",
            show_alert=True
        )
        return

    create_user_event(user_id, 'calculator_used', {'calculator': 'bmi'})
    # Рассчитываем BMI
    result = calculate_bmi(profile.current_weight, profile.height)

    # Форматируем результат
    message = format_bmi_result(result)

    await callback.message.edit_text(
        message,
        reply_markup=get_back_to_calculators()
    )
    await callback.answer()

@router.callback_query(F.data == "calc_calories")
async def calculate_calories_handler(callback: CallbackQuery):
    """Рассчитать калории и макросы"""
    user_id = callback.from_user.id
    profile = get_profile(user_id)

    if not profile:
        await callback.answer(
            "❌ Сначала создай профиль через /start",
            show_alert=True
        )
        return

    create_user_event(user_id, 'calculator_used', {'calculator': 'calories'})
    # Рассчитываем полное питание
    result = calculate_full_nutrition(
        weight=profile.current_weight,
        height=profile.height,
        age=profile.age,
        gender=profile.gender,
        activity_level=profile.activity_level,
        goal=profile.goal
    )

    # Форматируем результат
    message = format_calories_result(result)

    await callback.message.edit_text(
        message,
        reply_markup=get_back_to_calculators()
    )
    await callback.answer()

@router.callback_query(F.data == "calc_supplements")
async def calculate_supplements_handler(callback: CallbackQuery):
    """Рассчитать рекомендации по добавкам"""
    user_id = callback.from_user.id
    profile = get_profile(user_id)

    if not profile:
        await callback.answer(
            "❌ Сначала создай профиль через /start",
            show_alert=True
        )
        return

    create_user_event(user_id, 'calculator_used', {'calculator': 'supplements'})
    # Рассчитываем добавки
    result = calculate_supplement_recommendations(
        weight=profile.current_weight,
        goal=profile.goal,
        activity_level=profile.activity_level
    )

    # Форматируем результат
    message = format_supplements_result(result)

    # Telegram ограничивает длину сообщений до 4096 символов
    if len(message) > 4000:
        # Разбиваем на части
        parts = _split_long_message(message)
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # Последняя часть - с кнопками
                await callback.message.answer(part, reply_markup=get_back_to_calculators())
            else:
                await callback.message.answer(part)
        # Удаляем исходное сообщение
        await callback.message.delete()
    else:
        await callback.message.edit_text(
            message,
            reply_markup=get_back_to_calculators()
        )

    await callback.answer()

@router.callback_query(F.data == "supplements")
async def supplements_shortcut(callback: CallbackQuery):
    """Прямая ссылка на калькулятор добавок из главного меню"""
    await calculate_supplements_handler(callback)

def _split_long_message(message: str, max_length: int = 4000) -> list:
    """Разбить длинное сообщение на части"""
    if len(message) <= max_length:
        return [message]

    parts = []
    lines = message.split('\n')
    current_part = ""

    for line in lines:
        if len(current_part) + len(line) + 1 <= max_length:
            current_part += line + "\n"
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = line + "\n"

    if current_part:
        parts.append(current_part.strip())

    return parts
