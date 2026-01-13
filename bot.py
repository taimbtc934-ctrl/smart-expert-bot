import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# نقرأ التوكن من Environment Variable
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Free Signals", callback_data="free_signals")],
        [InlineKeyboardButton("Register", url="https://expertoption-track.com/379113545")]
    ])
    await update.message.reply_text(
        "👋 أهلاً بك في Smart Expert Signals Bot\n\n"
        "📊 نقدم إشارات وتحليلات تعليمية للتداول.\n"
        "⚠️ التداول ينطوي على مخاطر وليس ربحًا مضمونًا.",
        reply_markup=keyboard
    )

async def free_signals(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("🔹 Free Signal: BUY EUR/USD 1m")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(free_signals, pattern="free_signals"))

if __name__ == "__main__":
    app.run_polling()