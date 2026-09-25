import os
import base64
from io import BytesIO
from typing import Dict, List
from PIL import Image
from core.ai_provider import AIProviderError, chat_completion

async def recognize_food_from_image(image: Image.Image) -> Dict:
    """
    Распознать еду на фото через DeepSeek Vision

    Args:
        image: PIL Image объект

    Returns:
        Dict с информацией о распознанной еде
    """
    try:
        # Конвертируем изображение в base64
        image_base64 = _image_to_base64(image)

        # Промпт для vision-модели
        prompt = """Проанализируй это фото еды и предоставь детальную информацию:

1. Определи ВСЕ продукты/блюда на фото
2. Оцени размер порции для каждого продукта (в граммах или стандартных мерах)
3. Рассчитай калории для каждого продукта
4. Укажи макронутриенты (белки, жиры, углеводы) для каждого
5. Дай общий итог по калориям

Формат ответа (СТРОГО JSON):
{
    "detected_items": [
        {
            "name": "название продукта",
            "portion_size": "размер порции (например: 200г, 1 средняя порция)",
            "calories": число_калорий,
            "protein": граммы_белка,
            "fat": граммы_жира,
            "carbs": граммы_углеводов,
            "confidence": "высокая/средняя/низкая"
        }
    ],
    "total_calories": общее_число_калорий,
    "total_protein": общий_белок,
    "total_fat": общий_жир,
    "total_carbs": общие_углеводы,
    "accuracy_note": "примечание о точности оценки",
    "recommendations": ["рекомендация 1", "рекомендация 2"]
}

ВАЖНО:
- Если размер порции неясен, укажи это в accuracy_note
- Рекомендуй добавить на фото референсный объект (монета, ложка) для точности
- Погрешность расчета ±100-150 ккал - это нормально
- Если не уверен в продукте - укажи низкую уверенность (confidence: "низкая")
"""

        # Вызов DeepSeek Vision.
        response = await _call_vision(image_base64, prompt)

        # Парсим ответ
        result = _parse_vision_response(response)

        return result

    except Exception as e:
        return {
            'success': False,
            'error': f'Ошибка распознавания: {str(e)}',
            'message': 'Не удалось распознать еду на фото. Попробуйте сделать фото заново с лучшим освещением.'
        }

async def _call_vision(image_base64: str, prompt: str) -> str:
    """Call DeepSeek Vision without a vendor SDK."""
    try:
        return await chat_completion([
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {'type': 'image_url', 'image_url': {
                        'url': f'data:image/jpeg;base64,{image_base64}',
                        'detail': 'high',
                    }},
                ],
            }
        ], max_tokens=1500, temperature=0.3, vision=True)
    except AIProviderError as error:
        raise Exception(str(error)) from error

def _image_to_base64(image: Image.Image) -> str:
    """Конвертировать PIL Image в base64"""
    # Оптимизируем размер изображения для API
    max_size = (1024, 1024)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Конвертируем в JPEG
    buffered = BytesIO()
    image.convert('RGB').save(buffered, format="JPEG", quality=85)
    img_bytes = buffered.getvalue()

    return base64.b64encode(img_bytes).decode('utf-8')

def _parse_vision_response(response: str) -> Dict:
    """Парсинг ответа от vision-модели"""
    import json
    import re

    try:
        # Попытка извлечь JSON из ответа
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            data = json.loads(json_match.group())
        else:
            # Если JSON не найден, возвращаем текстовый ответ
            return {
                'success': False,
                'error': 'Не удалось распарсить ответ',
                'raw_response': response
            }

        # Формируем результат
        result = {
            'success': True,
            'detected_items': data.get('detected_items', []),
            'total_calories': data.get('total_calories', 0),
            'total_protein': data.get('total_protein', 0),
            'total_fat': data.get('total_fat', 0),
            'total_carbs': data.get('total_carbs', 0),
            'accuracy_note': data.get('accuracy_note', ''),
            'recommendations': data.get('recommendations', []),
            'confidence_level': _calculate_overall_confidence(data.get('detected_items', []))
        }

        return result

    except json.JSONDecodeError:
        return {
            'success': False,
            'error': 'Ошибка парсинга JSON ответа',
            'raw_response': response
        }

def _calculate_overall_confidence(items: List[Dict]) -> str:
    """Рассчитать общий уровень уверенности"""
    if not items:
        return "низкая"

    confidence_map = {"высокая": 3, "средняя": 2, "низкая": 1}
    avg_confidence = sum(confidence_map.get(item.get('confidence', 'низкая'), 1) for item in items) / len(items)

    if avg_confidence >= 2.5:
        return "высокая"
    elif avg_confidence >= 1.5:
        return "средняя"
    else:
        return "низкая"

def format_recognition_result(result: Dict) -> str:
    """
    Форматировать результат распознавания для отображения пользователю

    Args:
        result: результат распознавания

    Returns:
        Отформатированная строка для Telegram
    """
    if not result.get('success'):
        return f"❌ {result.get('error', 'Неизвестная ошибка')}\n\n{result.get('message', '')}"

    message = "🍽 <b>Распознанная еда:</b>\n\n"

    # Список продуктов
    for i, item in enumerate(result.get('detected_items', []), 1):
        confidence_emoji = {
            'высокая': '✅',
            'средняя': '⚠️',
            'низкая': '❓'
        }.get(item.get('confidence', 'средняя'), '⚠️')

        message += f"{i}. <b>{item['name']}</b> {confidence_emoji}\n"
        message += f"   Порция: {item['portion_size']}\n"
        message += f"   Калории: {item['calories']} ккал\n"
        message += f"   Б/Ж/У: {item['protein']}г / {item['fat']}г / {item['carbs']}г\n\n"

    # Итого
    message += "━━━━━━━━━━━━━━━━━\n"
    message += f"📊 <b>ИТОГО:</b>\n"
    message += f"🔥 Калории: {result['total_calories']} ккал\n"
    message += f"💪 Белки: {result['total_protein']}г\n"
    message += f"🥑 Жиры: {result['total_fat']}г\n"
    message += f"🍞 Углеводы: {result['total_carbs']}г\n\n"

    # Примечание о точности
    if result.get('accuracy_note'):
        message += f"ℹ️ <i>{result['accuracy_note']}</i>\n\n"

    # Рекомендации
    if result.get('recommendations'):
        message += "💡 <b>Рекомендации:</b>\n"
        for rec in result['recommendations']:
            message += f"• {rec}\n"

    # Уровень уверенности
    confidence_level = result.get('confidence_level', 'средняя')
    confidence_text = {
        'высокая': '✅ Высокая уверенность в распознавании',
        'средняя': '⚠️ Средняя уверенность - проверьте данные',
        'низкая': '❓ Низкая уверенность - рекомендуется корректировка'
    }.get(confidence_level, 'Средняя уверенность')

    message += f"\n{confidence_text}"

    return message

def adjust_portion(item: Dict, adjustment_factor: float) -> Dict:
    """
    Скорректировать порцию продукта

    Args:
        item: элемент из detected_items
        adjustment_factor: множитель (например, 0.5 для половины порции, 2 для двойной)

    Returns:
        Скорректированный элемент
    """
    adjusted = item.copy()
    adjusted['calories'] = round(item['calories'] * adjustment_factor)
    adjusted['protein'] = round(item['protein'] * adjustment_factor, 1)
    adjusted['fat'] = round(item['fat'] * adjustment_factor, 1)
    adjusted['carbs'] = round(item['carbs'] * adjustment_factor, 1)

    # Обновляем описание порции
    if adjustment_factor < 1:
        adjusted['portion_size'] = f"~{int(adjustment_factor * 100)}% от {item['portion_size']}"
    elif adjustment_factor > 1:
        adjusted['portion_size'] = f"~{int(adjustment_factor * 100)}% от {item['portion_size']}"

    return adjusted

def calculate_daily_totals(food_logs: List[Dict]) -> Dict:
    """
    Рассчитать общую статистику за день

    Args:
        food_logs: список записей о еде за день

    Returns:
        Суммарные данные
    """
    total = {
        'total_calories': 0,
        'total_protein': 0,
        'total_fat': 0,
        'total_carbs': 0,
        'meals_count': len(food_logs)
    }

    for log in food_logs:
        total['total_calories'] += log.get('total_calories', 0)
        total['total_protein'] += log.get('total_protein', 0)
        total['total_fat'] += log.get('total_fat', 0)
        total['total_carbs'] += log.get('total_carbs', 0)

    return total
