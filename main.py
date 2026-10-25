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
BOT_TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН"
ADMIN_ID = 8738748123 

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

# --- БОТ ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\nЭто бот для отслеживания цен.")

# --- API (Веб-сервер для расширения) ---
async def handle_add_item(request):
    # Заголовки для CORS (чтобы браузер разрешил запрос)
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    # Обработка preflight-запроса от браузера
    if request.method == 'OPTIONS':
        return web.Response(headers=headers)

    try:
        data = await request.json()
        url = data.get('url')
        target_price = data.get('target_price')
        
        bot = request.app['bot']
        await bot.send_message(
            ADMIN_ID,
            f"📦 <b>Новый товар добавлен!</b>\n"
            f"🔗 Ссылка: {url}\n"
            f"🎯 Желаемая цена: {target_price} ₽"
        )
        
        return web.json_response({"status": "ok"}, headers=headers)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=400, headers=headers)

async def start_web_server(bot):
    app = web.Application()
    app['bot'] = bot
    app.router.add_post('/api/add_item', handle_add_item)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Берем порт из переменной окружения (Bothost сам подставит)
    port = int(os.environ.get("PORT", 8080))
    
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Веб-сервер запущен на порту {port}")

# --- ЗАПУСК ---
async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # Запускаем веб-сервер
    await start_web_server(bot)
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
