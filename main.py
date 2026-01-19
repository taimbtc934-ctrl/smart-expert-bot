import json
import os
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================== CONFIG ==================
TOKEN = os.environ.get("BOT_TOKEN")  # Railway ENV
ADMIN_ID = 8057767905
CHANNEL_USERNAME = "@foranyone97"
DATA_FILE = "data.json"

# ================== DATA ==================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ================== LANG ==================
LANGS = {
    "ar": {
        "start": "👋 أهلاً بك في بوت الأدوات الذكية",
        "choose": "اختر من القائمة:",
        "bots": "🤖 قائمة البوتات",
        "vip": "👑 اشتراك VIP",
        "lang": "🌐 اللغة",
        "admin": "⚙️ لوحة الأدمن",
        "back": "⬅️ رجوع",
        "not_sub": "❌ يجب الاشتراك بالقناة أولاً",
    }
}

def get_lang(uid):
    return data["users"].get(str(uid), {}).get("lang", "ar")

def t(uid, key):
    return LANGS[get_lang(uid)].get(key, key)

# ================== USERS ==================
def ensure_user(uid):
    if str(uid) not in data["users"]:
        data["users"][str(uid)] = {
            "lang": "ar",
            "vip_until": None
        }
        save_data(data)

# ================== CHANNEL CHECK ==================
async def check_channel(uid, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, uid)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================== BOT DATABASE ==================
BOT_CATEGORIES = {
    "ai": {
        "name": "🤖 ذكاء اصطناعي",
        "bots": [
            ("ChatGPT Official", "@ChatGPT", "الدردشة مع GPT", "مجاني + Plus"),
            ("Grok AI", "@GrokAI", "ذكاء xAI مع صور وكود", "مجاني محدود"),
            ("Claude AI", "@ClaudeAIBot", "تحليل وكتابة احترافية", "مجاني محدود"),
            ("Gemini", "@GeminiTelegramBot", "مساعد Google", "مجاني"),
            ("AllQ", "@AllQBot", "عدة نماذج AI", "مجاني + مدفوع"),
        ],
    },
    "media": {
        "name": "📥 تحميل وميديا",
        "bots": [
            ("FileToBot", "@filetobot", "تخزين سحابي", "مجاني"),
            ("GetMediaBot", "@getmediabot", "تحميل سوشيال", "مجاني"),
            ("TikTok DL", "@tiktokdownloaderbot", "بدون علامة", "مجاني"),
            ("YouTube DL", "@youtubevideodownloaderbot", "جودات متعددة", "مجاني"),
            ("Spotify DL", "@SpotifyMusicDownloaderBot", "MP3", "مجاني"),
        ],
    },
    "tools": {
        "name": "🛠 أدوات وإنتاجية",
        "bots": [
            ("Skeddy", "@SkeddyBot", "تذكيرات ذكية", "مجاني"),
            ("Todo", "@todo", "مهام", "مجاني"),
            ("Translate", "@TranslateBot", "ترجمة فورية", "مجاني"),
            ("Weather", "@weatherbot", "طقس عالمي", "مجاني"),
            ("PDF Bot", "@pdfbot", "إدارة PDF", "مجاني + Pro"),
        ],
    },
    "groups": {
        "name": "👥 إدارة قروبات",
        "bots": [
            ("Rose", "@MissRose_bot", "حماية سبام", "مجاني"),
            ("Combot", "@combot", "إحصائيات", "مجاني + Pro"),
            ("GroupHelp", "@GroupHelpBot", "قواعد ومساعدة", "مجاني"),
        ],
    },
    "fun": {
        "name": "🎮 ترفيه",
        "bots": [
            ("Gamee", "@gamee", "ألعاب تنافسية", "مجاني"),
            ("Quiz", "@quizbot", "مسابقات", "مجاني"),
            ("MovieBot", "@moviebot", "بحث أفلام", "مجاني"),
            ("Currency", "@currencyconverterbot", "تحويل عملات", "مجاني"),
        ],
    },
}

# ================== MENUS ==================
def main_menu(uid):
    kb = [
        [InlineKeyboardButton(t(uid,"bots"), callback_data="bots")],
        [InlineKeyboardButton(t(uid,"vip"), callback_data="vip")],
        [InlineKeyboardButton(t(uid,"lang"), callback_data="lang")],
    ]
    if uid == ADMIN_ID:
        kb.append([InlineKeyboardButton(t(uid,"admin"), callback_data="admin")])
    return InlineKeyboardMarkup(kb)

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ensure_user(uid)

    if not await check_channel(uid, context):
        await update.message.reply_text(t(uid,"not_sub"))
        return

    await update.message.reply_text(
        f"{t(uid,'start')}\n\n{t(uid,'choose')}",
        reply_markup=main_menu(uid)
    )

# ================== CALLBACK ==================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    # BACK
    if q.data == "back":
        await q.edit_message_text(t(uid,"choose"), reply_markup=main_menu(uid))

    # CATEGORIES
    elif q.data == "bots":
        kb = [
            [InlineKeyboardButton(cat["name"], callback_data=f"cat_{k}")]
            for k, cat in BOT_CATEGORIES.items()
        ]
        kb.append([InlineKeyboardButton("⬅️ رجوع", callback_data="back")])
        await q.edit_message_text("📂 اختر التصنيف:", reply_markup=InlineKeyboardMarkup(kb))

    # BOT LIST
    elif q.data.startswith("cat_"):
        key = q.data.split("_")[1]
        bots = BOT_CATEGORIES[key]["bots"]
        kb = [
            [InlineKeyboardButton(b[0], callback_data=f"bot_{key}_{i}")]
            for i, b in enumerate(bots)
        ]
        kb.append([InlineKeyboardButton("⬅️ رجوع", callback_data="bots")])
        await q.edit_message_text("🤖 اختر البوت:", reply_markup=InlineKeyboardMarkup(kb))

    # BOT DETAILS
    elif q.data.startswith("bot_"):
        _, cat, idx = q.data.split("_")
        name, user, desc, status = BOT_CATEGORIES[cat]["bots"][int(idx)]
        text = (
            f"🤖 **{name}**\n\n"
            f"👤 {user}\n"
            f"📝 {desc}\n"
            f"⚡ الحالة: {status}"
        )
        kb = [
            [InlineKeyboardButton("🚀 دخول البوت", url=f"https://t.me/{user.replace('@','')}")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data=f"cat_{cat}")]
        ]
        await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

# ================== RUN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.run_polling()

if __name__ == "__main__":
    main()
