import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from groq import Groq


# =========================
# Flask Server برای Render
# =========================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "ربات روشنه 🤖"


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_flask, daemon=True).start()


# =========================
# گرفتن توکن ها از Render
# =========================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    print("❌ توکن ها در Environment Variables قرار نگرفته اند")
    exit()


# =========================
# Groq
# =========================

client = Groq(
    api_key=GROQ_API_KEY
)

MODEL = "llama-3.1-8b-instant"


SYSTEM_PROMPT = """
تو یک دستیار هوش مصنوعی فارسی زبان هستی.
به سوال های کاربر دوستانه و ساده جواب بده.
"""


# =========================
# تبلیغ
# =========================

PROMO = """
📢 کانفیگ پرسرعت

💰 قیمت: 75000 تومان

📞 09018830732
"""


def keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🛒 خرید کانفیگ",
                    url="https://t.me/+989018830732"
                )
            ]
        ]
    )


# =========================
# شروع
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "سلام 👋\n"
        "من ربات هوش مصنوعی هستم 🤖\n"
        "هر چیزی خواستی بپرس 😊\n\n"
        + PROMO,
        reply_markup=keyboard()
    )


# =========================
# جواب هوش مصنوعی
# =========================

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    try:

        result = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": update.message.text
                }
            ],
            max_tokens=500
        )


        await update.message.reply_text(
            result.choices[0].message.content
        )


    except Exception as e:

        print("ERROR:", e)

        await update.message.reply_text(
            "❌ خطا در اتصال به هوش مصنوعی"
        )


# =========================
# اجرا
# =========================

def main():

    bot = Application.builder().token(
        TELEGRAM_TOKEN
    ).build()


    bot.add_handler(
        CommandHandler("start", start)
    )


    bot.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            answer
        )
    )


    print("Bot is running...")

    bot.run_polling()


if __name__ == "__main__":
    main()
