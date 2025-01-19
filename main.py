import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.i18n import I18n
from aiohttp import web
from sqlalchemy.orm import sessionmaker

from bot.dispacher import TOKEN
from bot.handlers import dp
from bot.handlers.routine import scheduler
from bot.middilwares import all_middleware
from db import Config
from utils.config import WB

i18n = I18n(path="locales", default_locale="en", domain="messages")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Config.engine)


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{WB.BASE_WEBHOOK_URL}{WB.WEBHOOK_PATH}", secret_token=WB.WEBHOOK_SECRET)


async def main() -> web.Application:
    # TERMINALDA QILINADI AGAR HATOLIK BOLSA
    # 1) netstat -ano | findstr :8080
    # TCP    127.0.0.1:8080         0.0.0.0:0              LISTENING       <PID>
    # shunaqa narsa chiqsa
    # taskkill /PID <PID> /F yoki taskkill /PID 53436 /F
    # ngrok http 8080 bu orqali run qilinadi
    # bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # await all_middleware(dp, i18n)
    # app = web.Application()
    # webhook_requests_handler = SimpleRequestHandler(
    #     dispatcher=dp,
    #     bot=bot,
    #     secret_token=WB.WEBHOOK_SECRET,
    # )
    # webhook_requests_handler.register(app, path=WB.WEBHOOK_PATH)
    # setup_application(app, dp, bot=bot)
    # dp.startup.register(on_startup)
    #
    # return app
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await all_middleware(dp, i18n)
    await dp.start_polling(bot)


async def start_bot():
    scheduler.start()
    app = await main()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WB.WEB_SERVER_HOST, WB.WEB_SERVER_PORT)
    await site.start()
    print(f"Bot started and webhook listening at {WB.BASE_WEBHOOK_URL}{WB.WEBHOOK_PATH}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    # loop = asyncio.get_event_loop()            WEBHOOK
    # loop.run_until_complete(start_bot())       WEBHOOK
    try:
        asyncio.run(start_bot())
        # loop.run_forever()                     WEBHOOK
    except KeyboardInterrupt:
        print("Shutting down")
