# sokyrach_bot/main.py

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup  # Імпортуємо об'єкти для роботи з Telegram API
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler  # Хендлери та контексти для Telegram
from openai import OpenAI  # Імпортуємо OpenAI SDK

# --- Конфігурація ---
PORT = int(os.getenv("PORT", 8443))  # Порт для Webhook (за замовчуванням 8443)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # URL webhook-у, який вказується в Render
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Ключ OpenAI для генерації відповідей
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен Telegram-бота

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Ініціалізація клієнта OpenAI ---
openai = OpenAI(api_key=OPENAI_API_KEY)

# Функція генерації відповіді в стилі Сокирача
async def generate_sokyra_reply(user_input: str) -> str:
    prompt = f"""
    Ти — Сокирач. Грубий, мудрий, гнівний іронік. Ти відповідаєш коротко (до 3 рядків), рубаєш правду в лоб.
    Користувач запитує: "{user_input}"
    Відповідь Сокирача:
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",  # Використовуємо найновішу модель GPT-4o
            messages=[
                {"role": "system", "content": "Ти — персонаж Сокирач, який відповідає різко, коротко, мудро та емоційно."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,  # Температура для креативності
            max_tokens=150  # Максимальна довжина відповіді
        )
        return response.choices[0].message.content.strip()  # Повертаємо згенеровану відповідь
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return "Сокирач змовчав. Але щось він точно подумав."  # Помилка при генерації

# --- Хендлер команди /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💥 Рубани мені правду", callback_data="ask")]]  # Кнопка для запиту
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Я — Сокирач. Запитай щось — і я рубону тобі словом.",
        reply_markup=reply_markup  # Додаємо клавіатуру
    )

# --- Обробка натискання кнопки ---
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Підтвердження натискання
    await query.message.reply_text("Напиши мені свою думку, ситуацію або питання — і я скажу, як є.")

# --- Обробка текстових повідомлень користувача ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text  # Текст запиту від користувача
    await update.message.chat.send_action(action="typing")  # Анімація "друкування"
    response = await generate_sokyra_reply(user_input)  # Генеруємо відповідь GPT
    await update.message.reply_text(response)  # Надсилаємо відповідь користувачу

# --- Головна точка запуску ---
def main():
    application = Application.builder().token(BOT_TOKEN).build()  # Створюємо додаток Telegram

    # Реєструємо хендлери
    application.add_handler(CommandHandler("start", start))  # Команда /start
    application.add_handler(CallbackQueryHandler(handle_button))  # Кнопки
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Звичайні повідомлення

    # Запускаємо бот через webhook (не polling)
    application.run_webhook(
        listen="0.0.0.0",  # Приймаємо всі підключення
        port=PORT,  # Використовуємо порт з ENV або 8443
        url_path="",  # Не потрібен додатковий шлях
        webhook_url=WEBHOOK_URL  # Повний URL webhook-у
    )

# --- Запуск скрипту ---
if __name__ == "__main__":
    main()  # Викликаємо основну функцію
