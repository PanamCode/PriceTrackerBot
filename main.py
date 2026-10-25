import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web
import os

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8915572654:AAGR994EzZIPvf69KK5lOQRYVqZdtTQT494" 
ADMIN_ID = 8738748123  # Твой ID в Телеграме

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

# --- БОТ ---
@dp.message(F.text)
async def echo_handler(message: Message):
    await message.answer(f"Ты написал: {message.text}\nНо я бот для отслеживания цен. Напиши /start")
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"
        "Это бот для отслеживания цен Price Tracker.\n"
        "Скоро здесь будут уведомления о скидках."
    )

# --- API (Веб-сервер для расширения) ---
async def handle_add_item(request):
    try:
        data = await request.json()
        url = data.get('url')
        target_price = data.get('target_price')
        
        bot = request.app['bot']
        
        # Отправляем уведомление тебе в Телеграм
        await bot.send_message(
            ADMIN_ID,
            f"📦 <b>Новый товар добавлен!</b>\n"
            f"🔗 Ссылка: {url}\n"
            f"🎯 Желаемая цена: {target_price} ₽"
        )
        
        return web.json_response({"status": "ok"})
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=400)

async def start_web_server(bot):
    app = web.Application()
    app['bot'] = bot
    app.router.add_post('/api/add_item', handle_add_item)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Берем порт из переменной окружения (Bothost сам подставит нужный)
    port = int(os.environ.get("PORT", 8080))
    
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Веб-сервер запущен на порту {port}")

# --- ЗАПУСК ---
async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # Запускаем веб-сервер в фоне
    await start_web_server(bot)
    
    # Запускаем самого бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
