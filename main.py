import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web
import os

# --- НАСТРОЙКИ ---
BOT_TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН_ОТ_BOTFATHER"
ADMIN_ID = 8738748123 

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

# --- БОТ ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"
        "Это Price Tracker. Я слежу за ценами.\n\n"
        "Как добавить товар:\n"
        "1. Открой расширение в Chrome.\n"
        "2. Нажми 'Добавить'.\n"
        "3. Я пришлю уведомление, когда цена упадет."
    )

# Обработчик команды /add
@dp.message(Command("add"))
async def add_item(message: Message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer("Формат: /add [ссылка] [желаемая цена]")
            return
        
        url = parts[1]
        target_price = parts[2]
        
        # В будущем здесь будет сохранение в базу данных
        await message.answer(
            f"✅ <b>Товар добавлен в отслеживание!</b>\n"
            f"🔗 Ссылка: {url}\n"
            f"🎯 Желаемая цена: {target_price} ₽\n"
            f"Я пришлю уведомление, когда цена упадет."
        )
    except Exception as e:
        await message.answer("Ошибка. Проверь формат.")

# API (Веб-сервер, чтобы Bothost не ругался)
async def handle_root(request):
    return web.Response(text="Bot is running")

async def start_web_server(bot):
    app = web.Application()
    app['bot'] = bot
    app.router.add_get('/', handle_root)
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Веб-сервер запущен на порту {port}")

# --- ЗАПУСК ---
async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await start_web_server(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
