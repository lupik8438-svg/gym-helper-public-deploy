import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import MenuButtonWebApp, WebAppInfo

from bot.config import BOT_TOKEN, WEBAPP_PUBLIC_URL
from database.connection import init_db
from bot.handlers import start, registration, calculators, food_scanner, profile, help, control, programs

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""

    # Инициализация БД
    logger.info("Инициализация базы данных...")
    init_db()
    logger.info("База данных инициализирована ✅")

    # Создание бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Создание диспетчера
    dp = Dispatcher()

    # Регистрация роутеров (порядок важен!)
    dp.include_router(start.router)
    dp.include_router(control.router)
    dp.include_router(programs.router)
    dp.include_router(help.router)
    dp.include_router(registration.router)
    dp.include_router(profile.router)
    dp.include_router(calculators.router)
    dp.include_router(food_scanner.router)

    # Закрепляем Mini App в меню чата, если настроен публичный HTTPS-адрес.
    if WEBAPP_PUBLIC_URL.startswith("https://"):
        try:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="Gym Helper",
                    web_app=WebAppInfo(url=WEBAPP_PUBLIC_URL.rstrip("/")),
                )
            )
            logger.info("🚀 Mini App добавлен в меню Telegram: %s", WEBAPP_PUBLIC_URL)
        except Exception as error:
            logger.warning("Не удалось установить кнопку Mini App: %s", error)
    else:
        logger.warning("WEBAPP_PUBLIC_URL не настроен: Telegram не сможет открыть localhost")

    # Запуск
    logger.info("🤖 Бот запущен!")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
