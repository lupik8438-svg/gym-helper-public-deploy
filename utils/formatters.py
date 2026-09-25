"""Мобильные Telegram-форматтеры.

Telegram использует пропорциональный шрифт, а ширина emoji отличается,
поэтому здесь намеренно нет ASCII-рамок и широких таблиц.
"""
from typing import Dict


def _bar(value: float, total: float, size: int = 10) -> str:
    ratio = max(0, min(value / total, 1)) if total else 0
    filled = round(ratio * size)
    return f"{'▓' * filled}{'░' * (size - filled)} {ratio * 100:.0f}%"


def _divider() -> str:
    return "— — — — — — — —"


def _category_emoji(category: str) -> str:
    if category == 'Нормальный вес':
        return '✅'
    if category == 'Недостаток веса':
        return '⚠️'
    if category == 'Избыточный вес':
        return '⚠️'
    return '🔴'


def format_bmi_result(result: Dict) -> str:
    category = result.get('category', 'Без категории')
    return (
        "📊 <b>BMI / ИМТ</b>\n\n"
        f"🎯 Результат: <code>{result['bmi']}</code>\n"
        f"{_category_emoji(category)} <b>{category}</b>\n\n"
        f"{_divider()}\n"
        f"💡 <i>{result['recommendation']}</i>"
    )


def format_calories_result(result: Dict) -> str:
    macros = result['macros']
    return (
        "🔥 <b>КАЛОРИИ И БЖУ</b>\n\n"
        f"🎯 Цель: <b>{result['target_calories']} ккал</b> / день\n"
        f"{_bar(result['target_calories'], max(result['tdee'], 1))}\n\n"
        "📈 <b>Основа расчёта</b>\n"
        f"• BMR: <code>{result['bmr']} ккал</code>\n"
        f"• TDEE: <code>{result['tdee']} ккал</code>\n"
        f"• {result['activity_description']}\n\n"
        "🍽 <b>Баланс БЖУ</b>\n"
        f"💪 Белки: <b>{macros['protein']} г</b> · {macros['protein_percent']}%\n"
        f"🥑 Жиры: <b>{macros['fat']} г</b> · {macros['fat_percent']}%\n"
        f"🍞 Углеводы: <b>{macros['carbs']} г</b> · {macros['carbs_percent']}%\n\n"
        f"{_divider()}\n"
        f"💡 <i>{result['goal_description']}. Ориентир можно корректировать по динамике.</i>"
    )


def format_supplements_result(result: Dict) -> str:
    message = "💊 <b>РЕКОМЕНДАЦИИ</b>\n\n"
    groups = [('Высокий', '🔴 ВЫСОКИЙ'), ('Средний', '🟡 СРЕДНИЙ'), ('Низкий', '🟢 НИЗКИЙ')]
    for priority, title in groups:
        items = [item for item in result['recommendations'] if item.get('priority') == priority]
        if items:
            message += f"<b>{title} ПРИОРИТЕТ</b>\n"
            for item in items:
                message += _format_supplement_item(item)
            message += "\n"
    message += f"{_divider()}\n💰 {result['monthly_cost_estimate']}\n\n"
    if result.get('additional_info'):
        message += "💡 <b>Советы</b>\n" + ''.join(f"• {tip}\n" for tip in result['additional_info']) + "\n"
    message += f"⚠️ <i>{result['disclaimer']}</i>"
    if result.get('hormone_warning'):
        message += f"\n\n{result['hormone_warning']}"
    return message


def _format_supplement_item(supp: Dict) -> str:
    return (
        f"\n<b>{supp['name']}</b>\n"
        f"📌 {supp['dosage']}\n"
        f"⏰ {supp['timing']}\n"
        f"ℹ️ {supp['description']}\n"
        f"{supp['contraindications']}\n"
    )


def format_profile(profile: Dict, user_info: Dict) -> str:
    activity_labels = {'sedentary': '🛋 Сидячий', 'light': '🚶 Лёгкая', 'moderate': '🏃 Умеренная', 'active': '🏋️ Высокая', 'very_active': '💪 Очень высокая'}
    goal_labels = {'lose_weight': '📉 Похудение', 'maintain': '⚖️ Поддержание', 'gain_muscle': '📈 Набор массы'}
    exp_labels = {'beginner': '🌱 Новичок', 'intermediate': '💪 Средний', 'advanced': '🏆 Продвинутый'}
    return (
        "👤 <b>МОЙ ПРОФИЛЬ</b>\n\n"
        f"👋 <b>{user_info.get('first_name', 'Пользователь')}</b>\n"
        f"📅 С нами с: {user_info.get('created_at', 'недавно')}\n\n"
        "📊 <b>Параметры</b>\n"
        f"• Возраст: <code>{profile['age']} лет</code>\n"
        f"• Рост: <code>{profile['height']} см</code>\n"
        f"• Вес: <code>{profile['current_weight']} кг</code>\n"
        f"• Цель по весу: <code>{profile['target_weight']} кг</code>\n\n"
        "🎯 <b>Контекст</b>\n"
        f"• Цель: {goal_labels.get(profile['goal'], profile['goal'])}\n"
        f"• Активность: {activity_labels.get(profile['activity_level'], profile['activity_level'])}\n"
        f"• Опыт: {exp_labels.get(profile['experience_level'], profile['experience_level'])}\n"
        f"• Тренировки: <code>{profile.get('training_days_per_week') or '—'} / нед.</code>\n"
        f"• Сон: <code>{profile.get('sleep_hours') or '—'} ч</code>"
    )


def format_weight_history(history: list) -> str:
    if not history:
        return "📈 <b>ИСТОРИЯ ВЕСА</b>\n\nПока нет записей. Зафиксируй первый замер!"
    message = "📈 <b>ИСТОРИЯ ВЕСА</b>\n\n"
    for i, record in enumerate(history[:10], 1):
        date = record['recorded_at'].strftime('%d.%m.%Y')
        weight = record['weight']
        change = ''
        if i < len(history):
            diff = weight - history[i]['weight']
            if diff:
                change = f" · {'+' if diff > 0 else ''}{diff:.1f} кг"
            else:
                change = " · без изменений"
        message += f"{i}. <code>{date}</code> — <b>{weight} кг</b>{change}\n"
    if len(history) > 1:
        total_diff = history[0]['weight'] - history[-1]['weight']
        message += f"\n{_divider()}\n🎯 Всего: <b>{total_diff:+.1f} кг</b>"
    return message


def format_daily_food_stats(totals: Dict, target_calories: int = None) -> str:
    total = totals['total_calories']
    target_line = ''
    if target_calories:
        diff = total - target_calories
        target_line = (
            f"\n🎯 Цель: <code>{target_calories} ккал</code>\n"
            f"Отклонение: <b>{diff:+.0f} ккал</b>\n"
            f"{_bar(total, target_calories)}\n"
        )
    return (
        "📊 <b>СЕГОДНЯ</b>\n\n"
        f"🔥 Калории: <b>{total:.0f} ккал</b>{target_line}\n"
        f"🍽 Приёмов пищи: <b>{totals['meals_count']}</b>\n\n"
        f"💪 Белки: <b>{totals['total_protein']:.0f} г</b>\n"
        f"🥑 Жиры: <b>{totals['total_fat']:.0f} г</b>\n"
        f"🍞 Углеводы: <b>{totals['total_carbs']:.0f} г</b>"
    )
