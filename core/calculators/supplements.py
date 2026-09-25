from typing import Dict, List

def calculate_supplement_recommendations(weight: float, goal: str, activity_level: str) -> Dict:
    """
    Рассчитать рекомендации по спортивным добавкам

    Args:
        weight: вес в кг
        goal: цель (lose_weight/maintain/gain_muscle)
        activity_level: уровень активности

    Returns:
        Dict с рекомендациями по добавкам
    """
    recommendations = []

    # 1. ПРОТЕИН - основная добавка
    protein_multiplier = _get_protein_multiplier(goal, activity_level)
    protein_daily = round(weight * protein_multiplier, 1)

    recommendations.append({
        'name': '💪 Протеин',
        'dosage': f'{protein_daily}г в день',
        'timing': 'После тренировки или между приемами пищи',
        'description': 'Строительный материал для мышц. Помогает восстановлению и росту мышечной ткани.',
        'contraindications': '⚠️ Заболевания почек, аллергия на лактозу (выбирайте изолят или растительный протеин)',
        'priority': 'Высокий',
        'calculation': f'{weight} кг × {protein_multiplier} = {protein_daily}г'
    })

    # 2. ГЕЙНЕР — удобная еда для набора калорий, не обязательная добавка.
    if goal == 'gain_muscle':
        recommendations.append({
            'name': '🥤 Гейнер',
            'dosage': 'Порция по этикетке, только если не добираешь калории едой',
            'timing': 'Между приёмами пищи или после тренировки',
            'description': 'Смесь белка и углеводов. Сначала попробуй добирать энергию обычной едой; гейнер не гарантирует рост мышц.',
            'contraindications': '⚠️ Проверь состав, сахар и переносимость молочных продуктов; при диабете или заболеваниях ЖКТ обсуди со специалистом.',
            'priority': 'Низкий',
            'calculation': 'Опциональный продукт, не нужен при достаточной калорийности рациона.'
        })

    # 2. КРЕАТИН - для набора массы и силы
    if goal in ['gain_muscle', 'maintain'] and activity_level in ['moderate', 'active', 'very_active']:
        recommendations.append({
            'name': '⚡ Креатин моногидрат',
            'dosage': '5г в день',
            'timing': 'После тренировки с углеводами или в любое время дня',
            'description': 'Увеличивает силовые показатели, способствует росту мышечной массы и улучшает восстановление.',
            'contraindications': '⚠️ Заболевания почек. Пить много воды (2.5-3л в день)',
            'priority': 'Средний',
            'calculation': 'Стандартная дозировка 5г/день'
        })

    # 3. ОМЕГА-3 - для всех
    omega3_dosage = '2г' if activity_level in ['active', 'very_active'] else '1г'
    recommendations.append({
        'name': '🐟 Омега-3 (EPA+DHA)',
        'dosage': f'{omega3_dosage} в день',
        'timing': 'Во время еды',
        'description': 'Противовоспалительное действие, здоровье сердца и суставов, улучшение восстановления.',
        'contraindications': '⚠️ Прием антикоагулянтов (проконсультируйтесь с врачом)',
        'priority': 'Высокий',
        'calculation': f'{"Интенсивные тренировки" if activity_level in ["active", "very_active"] else "Стандарт"}'
    })

    # 4. ВИТАМИН D - для всех
    vitamin_d_dosage = '3000-4000 МЕ' if activity_level in ['active', 'very_active'] else '2000-3000 МЕ'
    recommendations.append({
        'name': '☀️ Витамин D3',
        'dosage': f'{vitamin_d_dosage} в день',
        'timing': 'Утром с жирной пищей',
        'description': 'Здоровье костей, иммунитет, синтез тестостерона, настроение.',
        'contraindications': '⚠️ Гиперкальциемия. Желательно сдать анализ крови перед приемом',
        'priority': 'Высокий',
        'calculation': 'Особенно важно в осенне-зимний период'
    })

    # 5. МАГНИЙ - для восстановления
    if activity_level in ['moderate', 'active', 'very_active']:
        recommendations.append({
            'name': '🧪 Магний (цитрат/глицинат)',
            'dosage': '300-500 мг в день',
            'timing': 'Вечером перед сном',
            'description': 'Улучшает качество сна, снижает стресс, предотвращает судороги, помогает восстановлению.',
            'contraindications': '⚠️ Заболевания почек, может вызвать послабление стула',
            'priority': 'Средний',
            'calculation': 'Для активно тренирующихся'
        })

    # 6. BCAA - для интенсивных тренировок или похудения
    if (goal == 'lose_weight' and activity_level in ['moderate', 'active', 'very_active']) or \
       (goal == 'gain_muscle' and activity_level in ['active', 'very_active']):
        recommendations.append({
            'name': '🏃 BCAA (аминокислоты)',
            'dosage': '5-10г',
            'timing': 'Перед/во время/после тренировки',
            'description': 'Предотвращает распад мышц, улучшает восстановление. Особенно полезно на диете или при длительных тренировках.',
            'contraindications': '⚠️ Не требуется при достаточном потреблении протеина (необязательная добавка)',
            'priority': 'Низкий',
            'calculation': 'Опциональная добавка'
        })

    # 7. ВИТАМИННО-МИНЕРАЛЬНЫЙ КОМПЛЕКС
    recommendations.append({
        'name': '💊 Мультивитамины',
        'dosage': 'Согласно инструкции',
        'timing': 'Утром с едой',
        'description': 'Базовая поддержка организма, восполнение дефицитов микронутриентов.',
        'contraindications': '⚠️ Не заменяет полноценное питание',
        'priority': 'Средний',
        'calculation': 'Страховка от дефицитов'
    })

    # Дополнительные рекомендации в зависимости от цели
    additional_info = _get_additional_recommendations(goal, activity_level)

    return {
        'recommendations': recommendations,
        'total_count': len(recommendations),
        'monthly_cost_estimate': _estimate_monthly_cost(recommendations),
        'additional_info': additional_info,
        'disclaimer': '⚠️ Это общая информация, не назначение врача. При возрасте до 18 лет не начинайте спортивные добавки без родителя и педиатра. Проверяйте состав и противопоказания.',
        'hormone_warning': '⛔ Тренболон, тестостерон и другие анаболические гормоны не являются спортпитом. Самостоятельное применение может нарушить гормональную и сердечно-сосудистую системы, фертильность, настроение и работу печени; мы не подбираем схемы или дозировки. Только медицинское назначение и наблюдение врача.'
    }

def _get_protein_multiplier(goal: str, activity_level: str) -> float:
    """Определить множитель для расчета протеина"""
    if goal == 'gain_muscle':
        if activity_level in ['active', 'very_active']:
            return 2.2  # Интенсивный набор массы
        return 2.0
    elif goal == 'lose_weight':
        if activity_level in ['moderate', 'active', 'very_active']:
            return 2.0  # На диете нужно больше белка
        return 1.8
    else:  # maintain
        if activity_level in ['active', 'very_active']:
            return 1.8
        return 1.6

def _get_additional_recommendations(goal: str, activity_level: str) -> List[str]:
    """Дополнительные рекомендации"""
    tips = []

    if goal == 'lose_weight':
        tips.append('🔥 На диете особенно важен протеин - он сохраняет мышцы и дает чувство сытости')
        tips.append('💧 Пейте 2.5-3 литра воды в день')
        tips.append('🥗 Добавки не заменяют правильное питание - контролируйте калории')

    elif goal == 'gain_muscle':
        tips.append('💪 Креатин - одна из самых эффективных добавок для набора массы')
        tips.append('🍚 Достаточно калорий и углеводов важнее добавок')
        tips.append('😴 Сон 7-9 часов критически важен для роста мышц')

    else:  # maintain
        tips.append('⚖️ Базовые добавки (протеин, омега-3, витамин D) покроют основные потребности')
        tips.append('🎯 Фокус на качестве питания, а не на количестве добавок')

    if activity_level in ['active', 'very_active']:
        tips.append('🏋️ При высоких нагрузках уделите внимание восстановлению (сон, магний, достаточно калорий)')

    tips.append('📊 Сдайте анализы крови (витамин D, железо, В12) для точной диагностики дефицитов')

    return tips

def _estimate_monthly_cost(recommendations: List[Dict]) -> str:
    """Примерная оценка стоимости добавок в месяц"""
    priority_costs = {
        'Высокий': 2000,  # Протеин, омега-3, витамин D
        'Средний': 1500,  # Креатин, магний, мультивитамины
        'Низкий': 800     # BCAA и прочее
    }

    high_priority_count = sum(1 for r in recommendations if r.get('priority') == 'Высокий')
    medium_priority_count = sum(1 for r in recommendations if r.get('priority') == 'Средний')
    low_priority_count = sum(1 for r in recommendations if r.get('priority') == 'Низкий')

    # Примерный расчет
    estimated = (high_priority_count * 700) + (medium_priority_count * 400) + (low_priority_count * 300)

    return f'≈ {estimated:,} руб/месяц (только приоритетные добавки)'

def get_supplement_priority_list(recommendations: List[Dict]) -> Dict:
    """
    Разделить добавки по приоритетам

    Returns:
        Dict с добавками по категориям приоритета
    """
    high_priority = [r for r in recommendations if r.get('priority') == 'Высокий']
    medium_priority = [r for r in recommendations if r.get('priority') == 'Средний']
    low_priority = [r for r in recommendations if r.get('priority') == 'Низкий']

    return {
        'high': high_priority,
        'medium': medium_priority,
        'low': low_priority,
        'advice': 'Начните с добавок высокого приоритета. Средний и низкий приоритет - по желанию и бюджету.'
    }
