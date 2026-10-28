import os
import requests
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

# === ВСТАВЬ СВОИ ДАННЫЕ ТУТ ===
TELEGRAM_TOKEN = "8915572654:AAGR994EzZIPvf69KK5lOQRYVqZdtTQT494"  # Например: 123456:ABC-DEF...
TELEGRAM_CHAT_ID = "8738748123"          # Например: 123456789
# ===============================

def send_telegram_message(text):
    """Отправляет сообщение в Телеграм"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Ошибка Telegram API: {response.text}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

# Этот блок принимает уведомления от Playerok
@app.post("/webhook")
async def playerok_webhook(request: Request):
    try:
        # Получаем данные от Playerok
        data = await request.json()
        
        # Проверяем, что это именно покупка (структура может меняться, мы вытаскиваем ключевые поля)
        # В реальности Playerok присылает разные события, мы фильтруем по типу, если нужно
        event_type = data.get("event", "unknown")
        item_name = data.get("item", {}).get("title", "Неизвестный товар")
        price = data.get("item", {}).get("price", "0")
        buyer = data.get("buyer", {}).get("username", "Неизвестный покупатель")

        # Если это не покупка (например, просто проверка сервера), игнорируем
        if event_type not in ["new_order", "purchase", "order_created"]:
            # Если Playerok присылает пустой запрос при проверке вебхука
            return {"status": "ignored"}

        # Формируем красивое сообщение
        text = (
            f"🔥 <b>НОВАЯ ПОКУПКА НА PLAYEROK!</b>\n\n"
            f"📦 <b>Товар:</b> {item_name}\n"
            f"💰 <b>Сумма:</b> {price} ₽\n"
            f"👤 <b>Покупатель:</b> {buyer}\n\n"
            f"⚡ <i>Срочно зайди на Playerok и выдай заказ!</i>"
        )

        # Отправляем в Телеграм
        send_telegram_message(text)
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Ошибка обработки вебхука: {e}")
        return {"status": "error", "message": str(e)}

# Этот блок нужен, чтобы сервер работал, когда его запустит Ботош
if __name__ == "__main__":
    print("Запуск сервера уведомлений...")
    # Ботош автоматически подставит нужный порт, если мы его не укажем,
    # но для локального теста используем 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
