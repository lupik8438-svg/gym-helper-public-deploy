"""
Вспомогательные функции для валидации и конвертации данных
"""
from typing import Optional, Tuple

def validate_age(age_str: str) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Валидация возраста

    Returns:
        (is_valid, age, error_message)
    """
    try:
        age = int(age_str)
        if age < 10 or age > 100:
            return False, None, "Возраст должен быть от 10 до 100 лет"
        return True, age, None
    except ValueError:
        return False, None, "Пожалуйста, введите число"

def validate_height(height_str: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Валидация роста

    Returns:
        (is_valid, height, error_message)
    """
    try:
        height = float(height_str)
        if height < 100 or height > 250:
            return False, None, "Рост должен быть от 100 до 250 см"
        return True, height, None
    except ValueError:
        return False, None, "Пожалуйста, введите число"

def validate_weight(weight_str: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Валидация веса

    Returns:
        (is_valid, weight, error_message)
    """
    try:
        weight = float(weight_str)
        if weight < 30 or weight > 300:
            return False, None, "Вес должен быть от 30 до 300 кг"
        return True, weight, None
    except ValueError:
        return False, None, "Пожалуйста, введите число"

def validate_target_weight(current_weight: float, target_weight_str: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Валидация целевого веса

    Returns:
        (is_valid, target_weight, error_message)
    """
    try:
        target_weight = float(target_weight_str)
        if target_weight < 30 or target_weight > 300:
            return False, None, "Целевой вес должен быть от 30 до 300 кг"

        # Проверяем, чтобы изменение было разумным (не более 50 кг разницы)
        diff = abs(target_weight - current_weight)
        if diff > 50:
            return False, None, "Разница между текущим и целевым весом не должна превышать 50 кг. Ставьте реалистичные цели!"

        return True, target_weight, None
    except ValueError:
        return False, None, "Пожалуйста, введите число"

def kg_to_lbs(kg: float) -> float:
    """Конвертация кг в фунты"""
    return kg * 2.20462

def lbs_to_kg(lbs: float) -> float:
    """Конвертация фунтов в кг"""
    return lbs / 2.20462

def cm_to_inches(cm: float) -> float:
    """Конвертация см в дюймы"""
    return cm / 2.54

def inches_to_cm(inches: float) -> float:
    """Конвертация дюймов в см"""
    return inches * 2.54

def format_number(num: float, decimals: int = 1) -> str:
    """Форматирование числа с округлением"""
    return f"{num:.{decimals}f}"

def calculate_bmi_category_emoji(bmi: float) -> str:
    """Получить эмодзи для категории BMI"""
    if bmi < 18.5:
        return "⚠️"
    elif 18.5 <= bmi < 25:
        return "✅"
    elif 25 <= bmi < 30:
        return "⚠️"
    else:
        return "🔴"

def calculate_weight_change_emoji(current: float, target: float) -> str:
    """Эмодзи для изменения веса"""
    if current > target:
        return "📉"  # Нужно худеть
    elif current < target:
        return "📈"  # Нужно набирать
    else:
        return "⚖️"  # Вес в норме

def sanitize_user_input(text: str) -> str:
    """Очистка пользовательского ввода от HTML и опасных символов"""
    # Удаляем HTML теги
    import re
    text = re.sub(r'<[^>]+>', '', text)
    # Ограничиваем длину
    return text[:500]

def is_valid_telegram_user_id(user_id: int) -> bool:
    """Проверка валидности Telegram user ID"""
    # Telegram user IDs - положительные целые числа
    return isinstance(user_id, int) and user_id > 0

def format_activity_level(level: str) -> str:
    """Человекочитаемое описание уровня активности"""
    levels = {
        'sedentary': 'Сидячий образ жизни (без тренировок)',
        'light': 'Легкая активность (1-3 тренировки в неделю)',
        'moderate': 'Умеренная активность (3-5 тренировок в неделю)',
        'active': 'Высокая активность (6-7 тренировок в неделю)',
        'very_active': 'Очень высокая активность (2 тренировки в день)'
    }
    return levels.get(level, level)

def format_goal(goal: str) -> str:
    """Человекочитаемое описание цели"""
    goals = {
        'lose_weight': 'Похудение',
        'maintain': 'Поддержание веса',
        'gain_muscle': 'Набор мышечной массы'
    }
    return goals.get(goal, goal)

def format_experience(experience: str) -> str:
    """Человекочитаемое описание опыта"""
    experiences = {
        'beginner': 'Новичок',
        'intermediate': 'Средний уровень',
        'advanced': 'Продвинутый'
    }
    return experiences.get(experience, experience)

def parse_callback_data(callback_data: str) -> Tuple[str, Optional[str]]:
    """
    Парсинг callback_data

    Формат: "action_value" или просто "action"
    Returns: (action, value)
    """
    parts = callback_data.split('_', 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], None


def validate_range(value_str: str, minimum: float, maximum: float, label: str, integer: bool = False):
    """Универсальная проверка числового поля профиля."""
    try:
        value = int(value_str) if integer else float(value_str)
    except (TypeError, ValueError):
        return False, None, f"{label}: введи число"
    if value < minimum or value > maximum:
        suffix = "" if integer else " с дробной частью при необходимости"
        return False, None, f"{label} должно быть от {minimum:g} до {maximum:g}{suffix}"
    return True, value, None
