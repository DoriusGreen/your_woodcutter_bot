# bot.py

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import openai

# --- Конфігурація ---
PORT = int(os.getenv("PORT", 8443))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = OPENAI_API_KEY

# Функція генерації відповіді в стилі Сокирача
async def generate_sokyra_reply(user_input: str) -> str:
    prompt = f"""
    Ти — Сокирач. Грубий, мудрий, трохи агресивний, з іронією і гострим язиком. Відповіді — короткі (до 3 рядків), як сокирний удар. Без води, без моралей. Твій стиль: поєднання мудрості, сарказму, гніву, іронії та філософії. 
    Твої відповіді мудрі, чіткі, влучні, цікаві, але при цьому по-справжньому корисні та глибокі. За потреби можеш приводити приклади, аналогії, метафори, тощо, якщо це вдало інтергрується в загальну відповідь на запитання. 
    Користувач запитує: "{user_input}"
    Сокирач відповідає:
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ти — персонаж Сокирач, який відповідає різко, коротко, мудро та емоційно."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return "Сокирач змовчав. Але щось він точно подумав."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💥 Рубани мені правду", callback_data="ask")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Я — Сокирач. Запитай щось — і я рубону тобі словом.",
        reply_markup=reply_markup
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Напиши мені свою думку, ситуацію або питання — і я скажу, як є.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await update.message.chat.send_action(action="typing")
    response = await generate_sokyra_reply(user_input)
    await update.message.reply_text(response)

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="",
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
