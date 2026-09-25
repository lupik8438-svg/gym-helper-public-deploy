from typing import Dict
from bot.config import ACTIVITY_LEVELS, GOAL_ADJUSTMENTS

def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """
    Рассчитать базовый метаболизм (BMR) по формуле Mifflin-St Jeor

    Args:
        weight: вес в кг
        height: рост в см
        age: возраст
        gender: пол (male/female)

    Returns:
        BMR в ккал/день
    """
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:  # female
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    return bmr

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Рассчитать общий расход энергии (TDEE)

    Args:
        bmr: базовый метаболизм
        activity_level: уровень активности

    Returns:
        TDEE в ккал/день
    """
    multiplier = ACTIVITY_LEVELS.get(activity_level, 1.2)
    return bmr * multiplier

def calculate_calories_for_goal(tdee: float, goal: str) -> float:
    """
    Рассчитать калории с учетом цели

    Args:
        tdee: общий расход энергии
        goal: цель (lose_weight/maintain/gain_muscle)

    Returns:
        Рекомендуемые калории в день
    """
    adjustment = GOAL_ADJUSTMENTS.get(goal, 0)
    return tdee + adjustment

def calculate_macros(calories: float, goal: str) -> Dict:
    """
    Рассчитать распределение макронутриентов

    Args:
        calories: калории в день
        goal: цель пользователя

    Returns:
        Dict с граммами белков, жиров, углеводов
    """
    if goal == 'lose_weight':
        # Похудение: больше белка, меньше углеводов
        protein_percent = 0.35
        fat_percent = 0.30
        carbs_percent = 0.35
    elif goal == 'gain_muscle':
        # Набор массы: много углеводов и белка
        protein_percent = 0.30
        fat_percent = 0.25
        carbs_percent = 0.45
    else:  # maintain
        # Поддержание: сбалансированное соотношение
        protein_percent = 0.30
        fat_percent = 0.30
        carbs_percent = 0.40

    # Конвертируем в граммы (1г белка = 4 ккал, 1г жира = 9 ккал, 1г углеводов = 4 ккал)
    protein_grams = round((calories * protein_percent) / 4)
    fat_grams = round((calories * fat_percent) / 9)
    carbs_grams = round((calories * carbs_percent) / 4)

    return {
        'protein': protein_grams,
        'fat': fat_grams,
        'carbs': carbs_grams,
        'protein_percent': int(protein_percent * 100),
        'fat_percent': int(fat_percent * 100),
        'carbs_percent': int(carbs_percent * 100)
    }

def calculate_full_nutrition(weight: float, height: float, age: int,
                            gender: str, activity_level: str, goal: str) -> Dict:
    """
    Полный расчет питания

    Returns:
        Dict со всеми расчетами
    """
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    target_calories = calculate_calories_for_goal(tdee, goal)
    macros = calculate_macros(target_calories, goal)

    # Описание уровня активности
    activity_descriptions = {
        'sedentary': 'Сидячий образ жизни',
        'light': 'Легкая активность (1-3 тренировки/неделю)',
        'moderate': 'Умеренная активность (3-5 тренировок/неделю)',
        'active': 'Высокая активность (6-7 тренировок/неделю)',
        'very_active': 'Очень высокая активность (2 тренировки/день)'
    }

    # Описание цели
    goal_descriptions = {
        'lose_weight': 'Похудение',
        'maintain': 'Поддержание веса',
        'gain_muscle': 'Набор мышечной массы'
    }

    return {
        'bmr': round(bmr),
        'tdee': round(tdee),
        'target_calories': round(target_calories),
        'macros': macros,
        'activity_description': activity_descriptions.get(activity_level, ''),
        'goal_description': goal_descriptions.get(goal, '')
    }
