# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# ================== الإعدادات ==================
TOKEN = "8556676844:AAGrJ6KxBNrqs0dpGR9Fva-S56E9urnxSpU"
ADMIN_ID = 8057767905
CHANNEL_USERNAME = "@foranyone97"
CURRENCY = "USD"

PAY_WEEK = "https://your-payment-link/week"
PAY_MONTH = "https://your-payment-link/month"
PAY_YEAR = "https://your-payment-link/year"

# ================== التخزين ==================
users_lang = {}
vip_users = {}  # user_id: expire_date

# ================== اللغات ==================
LANGS = {
    "ar": "🇸🇦 عربي",
    "en": "🇬🇧 English",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "de": "🇩🇪 Deutsch",
    "tr": "🇹🇷 Türkçe",
    "ru": "🇷🇺 Русский",
    "hi": "🇮🇳 Hindi"
}

TEXT = {
    "start": {
        "ar": "👋 أهلاً بك\nاختر من القائمة:",
        "en": "👋 Welcome\nChoose from menu:"
    },
    "vip": {
        "ar": "👑 اشتراك VIP\nاختر الخطة:",
        "en": "👑 VIP Subscription\nChoose a plan:"
    }
}

# ================== البوتات (40) ==================
BOTS = {
    "AI": [
        ("ChatGPT", "@ChatGPT"),
        ("Claude", "@ClaudeAIBot"),
        ("Gemini", "@GeminiTelegramBot"),
        ("Grok", "@GrokAI"),
        ("AllQ", "@AllQBot"),
    ],
    "Media": [
        ("YouTube", "@youtubevideodownloaderbot"),
        ("TikTok", "@tiktokdownloaderbot"),
        ("Instagram", "@instasave_bot"),
        ("Spotify", "@SpotifyMusicDownloaderBot"),
        ("GetMedia", "@getmediabot"),
    ],
    "Tools": [
        ("PDF", "@pdfbot"),
        ("Translate", "@TranslateBot"),
        ("Weather", "@weatherbot"),
        ("Currency", "@currencyconverterbot"),
        ("OCR", "@ocrbot"),
    ],
    "Groups": [
        ("Rose", "@MissRose_bot"),
        ("Combot", "@combot"),
        ("GroupHelp", "@GroupHelpBot"),
        ("Skeddy", "@SkeddyBot"),
        ("Feed", "@TheFeedReaderBot"),
    ],
    "Fun": [
        ("Gamee", "@gamee"),
        ("Quiz", "@quizbot"),
        ("GameBot", "@gamebot"),
        ("QuotLy", "@QuotLyBot"),
        ("Stickers", "@stickerdownloadbot"),
    ]
}

# ================== أدوات ==================
def get_lang(user_id):
    return users_lang.get(user_id, "ar")

def is_vip(user_id):
    if user_id in vip_users:
        if vip_users[user_id] > datetime.now():
            return True
        else:
            del vip_users[user_id]
    return False

async def check_channel(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================== القوائم ==================
def main_menu(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Bots", callback_data="bots")],
        [InlineKeyboardButton("👑 VIP", callback_data="vip")],
        [InlineKeyboardButton("🌐 Language", callback_data="lang")]
    ])

def back_btn():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]])

# ================== Handlers ==================
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_lang.setdefault(user.id, "ar")
    if not await check_channel(user.id, ctx.bot):
        await update.message.reply_text(f"❗ اشترك بالقناة أولاً {CHANNEL_USERNAME}")
        return
    await update.message.reply_text(
        TEXT["start"][get_lang(user.id)],
        reply_markup=main_menu(get_lang(user.id))
    )

async def buttons(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    lang = get_lang(uid)

    if q.data == "back":
        await q.edit_message_text(TEXT["start"][lang], reply_markup=main_menu(lang))

    elif q.data == "vip":
        await q.edit_message_text(
            TEXT["vip"][lang],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🟢 أسبوعي - 2$", url=PAY_WEEK)],
                [InlineKeyboardButton("🔵 شهري - 5$", url=PAY_MONTH)],
                [InlineKeyboardButton("🟣 سنوي - 50$", url=PAY_YEAR)],
                [InlineKeyboardButton("⬅️ رجوع", callback_data="back")]
            ])
        )

    elif q.data == "lang":
        kb = [[InlineKeyboardButton(v, callback_data=f"setlang_{k}")] for k, v in LANGS.items()]
        kb.append([InlineKeyboardButton("⬅️ رجوع", callback_data="back")])
        await q.edit_message_text("🌐 اختر اللغة:", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data.startswith("setlang_"):
        users_lang[uid] = q.data.split("_")[1]
        await q.edit_message_text("✅ تم تغيير اللغة", reply_markup=main_menu(users_lang[uid]))

    elif q.data == "bots":
        kb = []
        for cat, bots in BOTS.items():
            kb.append([InlineKeyboardButton(f"📂 {cat}", callback_data=f"cat_{cat}")])
        kb.append([InlineKeyboardButton("⬅️ رجوع", callback_data="back")])
        await q.edit_message_text("🤖 اختر الفئة:", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data.startswith("cat_"):
        cat = q.data.split("_")[1]
        kb = [[InlineKeyboardButton(f"{b[0]}", url=f"https://t.me/{b[1].replace('@','')}")] for b in BOTS[cat]]
        kb.append([InlineKeyboardButton("⬅️ رجوع", callback_data="bots")])
        await q.edit_message_text(f"📂 {cat}", reply_markup=InlineKeyboardMarkup(kb))

# ================== أدمن ==================
async def admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "⚙️ لوحة الأدمن",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
            [InlineKeyboardButton("➕ إضافة VIP", callback_data="addvip")],
            [InlineKeyboardButton("➖ حذف VIP", callback_data="delvip")]
        ])
    )

# ================== تشغيل ==================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(buttons))

    app.run_polling()