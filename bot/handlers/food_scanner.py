from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from PIL import Image
from io import BytesIO
import json

from database.crud import get_profile, create_food_log, get_food_logs_today, create_user_event
from core.calculators.food_recognition import (
    recognize_food_from_image,
    format_recognition_result,
    calculate_daily_totals
)
from core.calculators.calories import calculate_full_nutrition
from bot.keyboards import get_food_confirmation_keyboard, get_daily_stats_keyboard, get_main_menu
from bot.states import FoodScanStates
from utils.formatters import format_daily_food_stats

router = Router()

@router.callback_query(F.data == "scan_food")
async def start_food_scan(callback: CallbackQuery, state: FSMContext):
    """Начать сканирование еды"""
    user_id = callback.from_user.id
    profile = get_profile(user_id)

    if not profile:
        await callback.answer(
            "❌ Сначала создай профиль через /start",
            show_alert=True
        )
        return

    await state.set_state(FoodScanStates.waiting_for_photo)
    create_user_event(user_id, 'food_scan_started')

    await callback.message.edit_text(
        "📸 <b>Сканирование еды</b>\n\n"
        "Отправь мне фото своей еды, и я определю калорийность и макронутриенты!\n\n"
        "💡 <b>Советы для точного распознавания:</b>\n"
        "• Сделай фото сверху при хорошем освещении\n"
        "• Поместите рядом референсный объект (монета, ложка) для оценки размера\n"
        "• Убедись, что вся еда видна на фото\n\n"
        "📤 Отправь фото или нажми /cancel для отмены"
    )
    await callback.answer()

@router.message(FoodScanStates.waiting_for_photo, F.photo)
async def process_food_photo(message: Message, state: FSMContext):
    """Обработка фото еды"""
    # Отправляем сообщение о начале обработки
    processing_msg = await message.answer("🔍 Анализирую фото, подожди немного...")

    try:
        # Получаем фото в максимальном разрешении
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        photo_bytes = await message.bot.download_file(file.file_path)

        # Конвертируем в PIL Image
        image = Image.open(BytesIO(photo_bytes.read()))

        # Распознаём еду через подключённый vision-сервис
        result = await recognize_food_from_image(image)

        if not result.get('success'):
            await processing_msg.edit_text(
                f"❌ {result.get('error', 'Не удалось распознать еду')}\n\n"
                f"{result.get('message', 'Попробуй сделать фото заново с лучшим освещением.')}",
                reply_markup=get_main_menu()
            )
            await state.clear()
            return

        # Сохраняем результат в состоянии
        await state.update_data(
            recognition_result=result,
            photo_file_id=photo.file_id
        )

        # Форматируем результат для отображения
        formatted_result = format_recognition_result(result)

        await state.set_state(FoodScanStates.confirming_results)

        # Удаляем сообщение о обработке и отправляем результат
        await processing_msg.delete()
        await message.answer(
            formatted_result,
            reply_markup=get_food_confirmation_keyboard()
        )

    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Произошла ошибка при обработке фото:\n{str(e)}\n\n"
            "Попробуй еще раз или обратись в поддержку.",
            reply_markup=get_main_menu()
        )
        await state.clear()

@router.message(FoodScanStates.waiting_for_photo)
async def invalid_photo_input(message: Message):
    """Обработка неверного ввода (не фото)"""
    await message.answer(
        "❌ Пожалуйста, отправь <b>фото</b> своей еды.\n\n"
        "Или нажми /cancel для отмены."
    )

@router.callback_query(FoodScanStates.confirming_results, F.data == "food_confirm")
async def confirm_food_scan(callback: CallbackQuery, state: FSMContext):
    """Подтверждение результата и сохранение"""
    data = await state.get_data()
    result = data['recognition_result']
    photo_file_id = data['photo_file_id']

    user_id = callback.from_user.id

    # Сохраняем в базу данных
    food_log = create_food_log(
        user_id=user_id,
        photo_path=photo_file_id,
        detected_foods=json.dumps(result['detected_items'], ensure_ascii=False),
        total_calories=result['total_calories'],
        confirmed=True
    )

    await state.clear()

    # Получаем статистику за день
    profile = get_profile(user_id)
    daily_logs = get_food_logs_today(user_id)
    daily_totals = calculate_daily_totals(
        [{'total_calories': log.total_calories,
          'total_protein': result['total_protein'],
          'total_fat': result['total_fat'],
          'total_carbs': result['total_carbs']} for log in daily_logs]
    )

    # Рассчитываем целевые калории
    target_nutrition = calculate_full_nutrition(
        weight=profile.current_weight,
        height=profile.height,
        age=profile.age,
        gender=profile.gender,
        activity_level=profile.activity_level,
        goal=profile.goal
    )

    target_calories = target_nutrition['target_calories']

    # Форматируем статистику
    stats_message = format_daily_food_stats(daily_totals, target_calories)

    await callback.message.edit_text(
        f"✅ <b>Еда сохранена!</b>\n\n{stats_message}",
        reply_markup=get_daily_stats_keyboard()
    )
    await callback.answer("✅ Сохранено в дневник питания!")

@router.callback_query(FoodScanStates.confirming_results, F.data == "food_adjust")
async def adjust_food_portions(callback: CallbackQuery, state: FSMContext):
    """Корректировка порций (в упрощенной версии - просто предложение ввести вручную)"""
    await callback.answer(
        "ℹ️ Функция корректировки в разработке.\n"
        "Пока можешь отсканировать заново или подтвердить текущий результат.",
        show_alert=True
    )

@router.callback_query(FoodScanStates.confirming_results, F.data == "food_rescan")
async def rescan_food(callback: CallbackQuery, state: FSMContext):
    """Сканировать заново"""
    await state.set_state(FoodScanStates.waiting_for_photo)

    await callback.message.edit_text(
        "📸 <b>Отправь новое фото</b>\n\n"
        "Попробуй сделать фото при лучшем освещении или с другого угла."
    )
    await callback.answer()

@router.callback_query(FoodScanStates.confirming_results, F.data == "food_cancel")
async def cancel_food_scan(callback: CallbackQuery, state: FSMContext):
    """Отменить сканирование"""
    await state.clear()

    await callback.message.edit_text(
        "❌ Сканирование отменено.\n\n"
        "Выбери нужный раздел:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "daily_stats")
async def show_daily_stats(callback: CallbackQuery):
    """Показать статистику за день"""
    user_id = callback.from_user.id
    profile = get_profile(user_id)

    if not profile:
        await callback.answer(
            "❌ Профиль не найден",
            show_alert=True
        )
        return

    # Получаем записи за день
    daily_logs = get_food_logs_today(user_id)

    if not daily_logs:
        await callback.message.edit_text(
            "📊 <b>Статистика за сегодня</b>\n\n"
            "Пока нет записей о приемах пищи.\n"
            "Отсканируй свою еду, чтобы начать отслеживание!",
            reply_markup=get_main_menu()
        )
        await callback.answer()
        return

    # Рассчитываем итоги
    total_calories = sum(log.total_calories for log in daily_logs)

    # Получаем целевые калории
    target_nutrition = calculate_full_nutrition(
        weight=profile.current_weight,
        height=profile.height,
        age=profile.age,
        gender=profile.gender,
        activity_level=profile.activity_level,
        goal=profile.goal
    )

    target_calories = target_nutrition['target_calories']

    # Подсчитываем макросы (упрощенно - из сохраненных JSON)
    daily_totals = {
        'total_calories': total_calories,
        'total_protein': 0,
        'total_fat': 0,
        'total_carbs': 0,
        'meals_count': len(daily_logs)
    }

    for log in daily_logs:
        try:
            detected_foods = json.loads(log.detected_foods)
            for food in detected_foods:
                daily_totals['total_protein'] += food.get('protein', 0)
                daily_totals['total_fat'] += food.get('fat', 0)
                daily_totals['total_carbs'] += food.get('carbs', 0)
        except:
            pass

    # Форматируем статистику
    stats_message = format_daily_food_stats(daily_totals, target_calories)

    await callback.message.edit_text(
        stats_message,
        reply_markup=get_daily_stats_keyboard()
    )
    await callback.answer()

