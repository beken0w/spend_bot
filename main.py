import os
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher

from dotenv import load_dotenv

from routers.welcome import router1, start_bot, stop_bot
from routers.categories import router_cat
from routers.spendings import router_spd
from routers.reports import router_rpt

from aiogram.types import BotCommand


bot_commands = [
    BotCommand(command="/menu", description="Main menu")
]

logging.basicConfig(level=logging.DEBUG,
                    filename='log_file.log',
                    filemode='a',
                    encoding='utf-8')

load_dotenv()
TOKEN = os.getenv('TOKEN')

async def start():
    bot = Bot(TOKEN)
    dp = Dispatcher()
    await bot.set_my_commands(bot_commands)
    
    # при запуске и остановке выводит сообщение админу
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    
    dp.include_routers(router1, router_cat, router_spd, router_rpt)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        date_time = datetime.now().replace(microsecond=0)
        logging.info(f"\n{'='*30}[ {date_time} ]{'='*30}\n")
        logging.info("TOKEN - OK, Launch Bot")
        await dp.start_polling(bot)
        

    finally:
        await bot.session.close()
        logging.info("Bot stopped")


if __name__ == '__main__':
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        print("Bot stopped by Admin")
