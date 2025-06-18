import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random
from datetime import datetime
import pytz
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
USERS = [
    {"chat_id": 123456789, "name": "Имя", "city": "Warsaw", "timezone": "Europe/Warsaw"},
    # добавь других пользователей по аналогии
]

PREDICTIONS = [
    "Сегодня тебе улыбнется удача!",
    "Будь осторожен в пути.",
    "Жди хорошие новости вечером.",
    "Идеальный день, чтобы начать что-то новое!"
]

def get_weather(city: str) -> str:
    # заглушка — можно подключить реальный API позже
    return f"Погода в {city}: +20°C, облачно"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен!")

async def send_weather(app):
    now = datetime.now(pytz.utc)
    for user in USERS:
        if not user["chat_id"]:
            continue
        local_tz = pytz.timezone(user["timezone"])
        local_now = now.astimezone(local_tz)
        if local_now.hour != 7 or local_now.minute > 10:
            continue
        weather = get_weather(user["city"])
        prediction = random.choice(PREDICTIONS)
        message = f"{user['name']}, доброе утро!\n\n{weather}\n\nПредсказание: {prediction}"
        try:
            await app.bot.send_message(chat_id=user["chat_id"], text=message)
        except Exception as e:
            print(f"Ошибка при отправке пользователю {user['name']}: {e}")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(send_weather(app)), "interval", minutes=10)
    scheduler.start()

    print("Бот запущен")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
