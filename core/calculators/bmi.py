from typing import Dict

def calculate_bmi(weight: float, height: float) -> Dict:
    """
    Рассчитать индекс массы тела

    Args:
        weight: вес в кг
        height: рост в см

    Returns:
        Dict с BMI и интерпретацией
    """
    height_m = height / 100
    bmi = weight / (height_m ** 2)

    # Интерпретация
    if bmi < 18.5:
        category = "Недостаток веса"
        recommendation = "Рекомендуется увеличить калорийность питания и обратиться к врачу"
    elif 18.5 <= bmi < 25:
        category = "Нормальный вес"
        recommendation = "Отличный результат! Поддерживайте текущий образ жизни"
    elif 25 <= bmi < 30:
        category = "Избыточный вес"
        recommendation = "Рекомендуется небольшой дефицит калорий и регулярные тренировки"
    else:
        category = "Ожирение"
        recommendation = "Рекомендуется консультация с врачом и диетологом"

    return {
        "bmi": round(bmi, 1),
        "category": category,
        "recommendation": recommendation
    }
