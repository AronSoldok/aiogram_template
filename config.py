from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage


class Settings:
    load_dotenv()
    BOT_TOKEN: str = str(getenv('BOT_TOKEN'))
    # Список ID администраторов - для отладки добавим значение по умолчанию
    ADMINS: list = (
        [
            admin.strip()
            for admin in str(getenv("ADMINS", "")).split(",")
            if admin.strip()
        ]
        if str(getenv("ADMINS", ""))
        else []
    )
    POSTGRES_HOST: str = str(getenv("POSTGRES_HOST"))
    POSTGRES_PORT: int = int(str(getenv("POSTGRES_PORT")))
    POSTGRES_DB: str = str(getenv("POSTGRES_DB"))
    POSTGRES_USER: str = str(getenv("POSTGRES_USER"))
    POSTGRES_PASSWORD: str = str(getenv("POSTGRES_PASSWORD"))

    bot = Bot(
        token=BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True)
    )

    dp = Dispatcher(storage=MemoryStorage())

    database_models = [
        "database.models.base",
        "database.models.user",
    ]

    TORTOISE_ORM = {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "database": POSTGRES_DB,
                    "host": POSTGRES_HOST,
                    "password": POSTGRES_PASSWORD,
                    "port": POSTGRES_PORT,
                    "user": POSTGRES_USER,
                }
            }
        },
        "apps": {
            "models": {
                "models": database_models,
                "default_connection": "default"
            }
        }
    }

settings = Settings()
