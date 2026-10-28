from fastapi import FastAPI, Request
import requests
import uvicorn

app = FastAPI()

# ТВОИ ДАННЫЕ
TELEGRAM_TOKEN = "8915572654:AAGR994EzZIPvf69KK5lOQRYVqZdtTQT494"
TELEGRAM_CHAT_ID = "8738748123"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка отправки в ТГ: {e}")

@app.post("/webhook")
async def playerok_webhook(request: Request):
    try:
        data = await request.json()
        # Пример того, что может прийти от Playerok (зависит от настроек API)
        item_name = data.get("item_name", "Неизвестный товар")
        price = data.get("price", "0")
        buyer = data.get("buyer", "Покупатель")
        
        text = f"🔥 <b>НОВАЯ ПРОДАЖА НА PLAYEROK!</b>\n\n" \
               f"📦 Товар: {item_name}\n" \
               f"💰 Сумма: {price}₽\n" \
               f"👤 Покупатель: {buyer}\n\n" \
               f"👉 Срочно проверь сайт и выдай заказ!"
               
        send_telegram_message(text)
        return {"status": "ok"}
    except Exception as e:
        print(f"Ошибка обработки: {e}")
        return {"status": "error"}

if __name__ == "__main__":
    print("Сервер оповещений запущен на порту 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
