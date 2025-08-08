import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from tortoise import Tortoise

from config import settings
from schedulers.debt_reminder_scheduler import debt_scheduler
from handlers import setup_routers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def init_db():
    """Инициализация базы данных"""
    await Tortoise.init(config=settings.TORTOISE_ORM)
    await Tortoise.generate_schemas()
    logger.info("База данных инициализирована")


async def close_db():
    """Закрытие соединения с базой данных"""
    await Tortoise.close_connections()
    logger.info("Соединение с базой данных закрыто")

async def set_bot_commands(bot: Bot):
    """Устанавливает команды бота для отображения в меню автодополнения"""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Команды бота установлены")

async def main():
    """Основная функция запуска бота"""
    try:
        # Проверяем наличие плана в Circuit (создаём при отсутствии)
        from handlers.API.create_plan import ensure_plan_exists
        await ensure_plan_exists()
        
        # Инициализация базы данных
        await init_db()
        
        # Настройка команд бота
        await set_bot_commands(settings.bot)

        # Настройка роутеров
        setup_routers(settings.dp)
        
        # Запуск планировщика уведомлений о долгах
        debt_scheduler.start()
        logger.info("Планировщик уведомлений о долгах запущен")
        
        # Запуск процессора задач Google Sheets
        from handlers.API.API_GOOGLE_SHEETS.queue import task_processor
        import asyncio
        asyncio.create_task(task_processor.run_forever())
        logger.info("Процессор задач Google Sheets запущен")
        
        # Планировщик постановки задач Google Sheets
        from schedulers.google_sync_scheduler import scheduler_loop
        asyncio.create_task(scheduler_loop())
        logger.info("Планировщик задач Google Sheets запущен")
        
        # Запуск бота
        logger.info("Запуск бота...")
        await settings.dp.start_polling(settings.bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        
        # Закрытие базы данных
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
