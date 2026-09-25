#!/usr/bin/env python3
"""
Скрипт для проверки работоспособности всех компонентов бота
"""
import sys
import os

def check_imports():
    """Проверка импортов всех модулей"""
    print("🔍 Проверка импортов...")

    try:
        # Основные библиотеки
        import aiogram
        print("✅ aiogram")

        import sqlalchemy
        print("✅ sqlalchemy")

        import openai
        print("✅ openai")

        from PIL import Image
        print("✅ Pillow")

        import dotenv
        print("✅ python-dotenv")

        # Проверка модулей бота
        from bot.config import BOT_TOKEN, OPENAI_API_KEY
        print("✅ bot.config")

        from database.models import User, Profile, WeightHistory, FoodLog
        print("✅ database.models")

        from database.crud import get_user, create_profile
        print("✅ database.crud")

        from core.calculators.bmi import calculate_bmi
        print("✅ core.calculators.bmi")

        from core.calculators.calories import calculate_full_nutrition
        print("✅ core.calculators.calories")

        from core.calculators.supplements import calculate_supplement_recommendations
        print("✅ core.calculators.supplements")

        from core.calculators.food_recognition import recognize_food_from_image
        print("✅ core.calculators.food_recognition")

        from utils.formatters import format_bmi_result
        print("✅ utils.formatters")

        from utils.helpers import validate_age
        print("✅ utils.helpers")

        print("\n✅ Все импорты успешны!\n")
        return True

    except ImportError as e:
        print(f"\n❌ Ошибка импорта: {e}\n")
        return False

def check_config():
    """Проверка конфигурации"""
    print("🔍 Проверка конфигурации...")

    from bot.config import BOT_TOKEN, OPENAI_API_KEY, DATABASE_URL

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не установлен в .env")
        return False
    else:
        print(f"✅ BOT_TOKEN установлен ({BOT_TOKEN[:10]}...)")

    if not OPENAI_API_KEY:
        print("⚠️  OPENAI_API_KEY не установлен (сканирование еды не будет работать)")
    else:
        print(f"✅ OPENAI_API_KEY установлен ({OPENAI_API_KEY[:10]}...)")

    print(f"✅ DATABASE_URL: {DATABASE_URL}")

    print("\n✅ Конфигурация проверена!\n")
    return True

def test_calculators():
    """Тест калькуляторов"""
    print("🔍 Тестирование калькуляторов...")

    from core.calculators.bmi import calculate_bmi
    from core.calculators.calories import calculate_full_nutrition
    from core.calculators.supplements import calculate_supplement_recommendations

    # Тест BMI
    bmi_result = calculate_bmi(75, 180)
    assert 'bmi' in bmi_result
    print(f"✅ BMI: {bmi_result['bmi']}")

    # Тест калорий
    calories_result = calculate_full_nutrition(
        weight=75, height=180, age=25, gender='male',
        activity_level='moderate', goal='maintain'
    )
    assert 'target_calories' in calories_result
    print(f"✅ Калории: {calories_result['target_calories']} ккал")

    # Тест добавок
    supplements_result = calculate_supplement_recommendations(
        weight=75, goal='gain_muscle', activity_level='active'
    )
    assert 'recommendations' in supplements_result
    print(f"✅ Добавки: {len(supplements_result['recommendations'])} рекомендаций")

    print("\n✅ Все калькуляторы работают!\n")
    return True

def test_database():
    """Тест базы данных"""
    print("🔍 Тестирование базы данных...")

    from database.connection import init_db, SessionLocal
    from database.models import User, Profile

    # Инициализация БД
    init_db()
    print("✅ База данных инициализирована")

    # Проверка подключения
    db = SessionLocal()
    try:
        # Простой запрос
        count = db.query(User).count()
        print(f"✅ Подключение к БД работает (пользователей: {count})")
    finally:
        db.close()

    print("\n✅ База данных работает!\n")
    return True

def test_formatters():
    """Тест форматтеров"""
    print("🔍 Тестирование форматтеров...")

    from utils.formatters import format_bmi_result, format_calories_result
    from utils.helpers import validate_age, validate_weight

    # Тест валидации
    is_valid, age, error = validate_age("25")
    assert is_valid and age == 25
    print("✅ Валидация возраста")

    is_valid, weight, error = validate_weight("75.5")
    assert is_valid and weight == 75.5
    print("✅ Валидация веса")

    # Тест форматирования
    bmi_result = {'bmi': 23.1, 'category': 'Нормальный вес', 'recommendation': 'Отлично!'}
    formatted = format_bmi_result(bmi_result)
    assert 'BMI' in formatted
    print("✅ Форматирование BMI")

    print("\n✅ Форматтеры работают!\n")
    return True

def main():
    """Главная функция"""
    print("=" * 60)
    print("🤖 FitBot - Проверка работоспособности")
    print("=" * 60)
    print()

    all_passed = True

    # Проверка импортов
    if not check_imports():
        all_passed = False
        print("❌ Установите недостающие зависимости: pip install -r requirements.txt\n")

    # Проверка конфигурации
    if all_passed:
        if not check_config():
            all_passed = False
            print("❌ Настройте .env файл\n")

    # Тест базы данных
    if all_passed:
        try:
            if not test_database():
                all_passed = False
        except Exception as e:
            print(f"❌ Ошибка БД: {e}\n")
            all_passed = False

    # Тест калькуляторов
    if all_passed:
        try:
            if not test_calculators():
                all_passed = False
        except Exception as e:
            print(f"❌ Ошибка калькуляторов: {e}\n")
            all_passed = False

    # Тест форматтеров
    if all_passed:
        try:
            if not test_formatters():
                all_passed = False
        except Exception as e:
            print(f"❌ Ошибка форматтеров: {e}\n")
            all_passed = False

    # Итоговый результат
    print("=" * 60)
    if all_passed:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print()
        print("Бот готов к запуску:")
        print("  python main.py")
        print()
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print()
        print("Исправьте ошибки перед запуском бота")
        print()
    print("=" * 60)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
