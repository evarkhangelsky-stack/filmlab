import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN
from database import init_db
from handlers import router as user_router
from admin_handlers import router as admin_router

logging.basicConfig(level=logging.INFO)

async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(user_router)
    dp.include_router(admin_router)
    await bot.set_my_commands([
        BotCommand(command="start", description="Launch THE LAB"),
    ])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
