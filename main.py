import asyncio
import logging
from aiogram import Bot
from aiogram.types import BotCommand
from tortoise import Tortoise

from config import settings
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
        # Инициализация базы данных
        await init_db()
        
        # Настройка команд бота
        await set_bot_commands(settings.bot)
        
        logger.info("Запуск бота...")
        await settings.dp.start_polling(settings.bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        # Закрытие базы данных
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
