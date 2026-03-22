import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")
    def log_message(self, format, *args):
        return

def run_web():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=run_web, daemon=True).start()

import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8522320066:AAHsXLyhD9qWdhatfg3sbDDVgIFmD98RQz8"
ADMIN_ID = 585022030
CHANNEL_LINK = "https://t.me/premium_uzmarket"
# ======================

# ===== ПРАЙС-ЛИСТ =====
PREMIUM_PRICES = {
    "1 месяц / 1 oy": "35 000 сум",
    "3 месяца / 3 oy": "90 000 сум",
    "6 месяцев / 6 oy": "160 000 сум",
    "12 месяцев / 12 oy": "290 000 сум",
}

STARS_PRICES = {
    "50 Stars": "10 000 сум",
    "100 Stars": "18 000 сум",
    "250 Stars": "40 000 сум",
    "500 Stars": "75 000 сум",
    "1000 Stars": "140 000 сум",
}

PAYMENT_DETAILS = "9860 1666 0370 5616 (Uzcard)"
# ========================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("💎 Telegram Premium", callback_data="menu_premium")],
        [InlineKeyboardButton("⭐ Telegram Stars", callback_data="menu_stars")],
        [InlineKeyboardButton("📞 Поддержка / Yordam", callback_data="support")],
    ]
    await update.message.reply_text(
        "👋 Добро пожаловать в Premium & Stars!\n"
        "👋 Premium & Stars ga xush kelibsiz!\n\n"
        "🌟 Покупай Telegram Premium и Stars по лучшим ценам в Узбекистане.\n"
        "🌟 O'zbekistondagi eng yaxshi narxlarda Telegram Premium va Stars sotib oling.\n\n"
        "Выбери / Tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        context.user_data.clear()
        keyboard = [
            [InlineKeyboardButton("💎 Telegram Premium", callback_data="menu_premium")],
            [InlineKeyboardButton("⭐ Telegram Stars", callback_data="menu_stars")],
            [InlineKeyboardButton("📞 Поддержка / Yordam", callback_data="support")],
        ]
        await query.edit_message_text(
            "👋 Добро пожаловать в Premium & Stars!\n"
            "👋 Premium & Stars ga xush kelibsiz!\n\n"
            "🌟 Покупай Telegram Premium и Stars по лучшим ценам в Узбекистане.\n"
            "🌟 O'zbekistondagi eng yaxshi narxlarda Telegram Premium va Stars sotib oling.\n\n"
            "Выбери / Tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "menu_premium":
        text = "💎 **Telegram Premium**\n\n"
        for period, price in PREMIUM_PRICES.items():
            text += f"▫️ {period} — **{price}**\n"
        text += "\nВыбери срок / Muddatni tanlang:"

        keyboard = []
        for period in PREMIUM_PRICES:
            keyboard.append([InlineKeyboardButton(
                f"💎 {period} — {PREMIUM_PRICES[period]}",
                callback_data=f"buy_prem_{period}"
            )])
        keyboard.append([InlineKeyboardButton("⬅️ Назад / Ortga", callback_data="main_menu")])

        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

    elif data == "menu_stars":
        text = "⭐ **Telegram Stars**\n\n"
        for amount, price in STARS_PRICES.items():
            text += f"▫️ {amount} — **{price}**\n"
        text += "\nВыбери количество / Miqdorni tanlang:"

        keyboard = []
        for amount in STARS_PRICES:
            keyboard.append([InlineKeyboardButton(
                f"⭐ {amount} — {STARS_PRICES[amount]}",
                callback_data=f"buy_star_{amount}"
            )])
        keyboard.append([InlineKeyboardButton("⬅️ Назад / Ortga", callback_data="main_menu")])

        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

    elif data.startswith("buy_prem_"):
        period = data.replace("buy_prem_", "")
        price = PREMIUM_PRICES.get(period, "?")
        context.user_data["order"] = {"type": "Premium", "item": period, "price": price}
        context.user_data["step"] = "waiting_username"

        await query.edit_message_text(
            f"💎 **Заказ / Buyurtma: Telegram Premium — {period}**\n"
            f"💰 Сумма / Narx: **{price}**\n\n"
            f"👤 Напишите username аккаунта, на который отправить Premium\n"
            f"👤 Premium yuboriladigan username ni yozing\n"
            f"(например / masalan: @username)",
            parse_mode="Markdown"
        )

    elif data.startswith("buy_star_"):
        amount = data.replace("buy_star_", "")
        price = STARS_PRICES.get(amount, "?")
        context.user_data["order"] = {"type": "Stars", "item": amount, "price": price}
        context.user_data["step"] = "waiting_username"

        await query.edit_message_text(
            f"⭐ **Заказ / Buyurtma: {amount}**\n"
            f"💰 Сумма / Narx: **{price}**\n\n"
            f"👤 Напишите username аккаунта, на который отправить Stars\n"
            f"👤 Stars yuboriladigan username ni yozing\n"
            f"(например / masalan: @username)",
            parse_mode="Markdown"
        )

    elif data == "support":
        keyboard = [
            [InlineKeyboardButton("📢 Канал / Kanal", url=CHANNEL_LINK)],
            [InlineKeyboardButton("⬅️ Назад / Ortga", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "📞 **Поддержка / Yordam**\n\n"
            "Если есть вопросы — напиши админу или зайди в канал.\n"
            "Savollar bo'lsa — adminga yozing yoki kanalga kiring.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")

    if step == "waiting_username":
        username = update.message.text.strip()
        if not username.startswith("@"):
            username = "@" + username
        context.user_data["target_username"] = username
        context.user_data["step"] = "waiting_screenshot"

        order = context.user_data.get("order", {})
        await update.message.reply_text(
            f"✅ Аккаунт / Akkaunt: **{username}**\n\n"
            f"📌 Оплатите и отправьте скриншот:\n"
            f"📌 To'lang va skrinshot yuboring:\n\n"
            f"💳 Реквизиты / Karta:\n"
            f"`{PAYMENT_DETAILS}`\n"
            f"💰 Сумма / Narx: **{order.get('price', '?')}**\n\n"
            f"📸 Отправьте скриншот сюда / Skrinshot yuboring 👇",
            parse_mode="Markdown"
        )

    elif step == "waiting_screenshot":
        await update.message.reply_text(
            "📸 Отправьте скриншот оплаты (фото).\n"
            "📸 To'lov skrinshotini yuboring (rasm)."
        )

    else:
        keyboard = [
            [InlineKeyboardButton("💎 Telegram Premium", callback_data="menu_premium")],
            [InlineKeyboardButton("⭐ Telegram Stars", callback_data="menu_stars")],
        ]
        await update.message.reply_text(
            "Выбери что хочешь купить / Nimani sotib olmoqchisiz:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")

    if step != "waiting_screenshot":
        return

    user = update.message.from_user
    order = context.user_data.get("order", {})
    target = context.user_data.get("target_username", "не указан")
    photo = update.message.photo[-1]

    context.user_data["step"] = "done"

    await update.message.reply_text(
        "✅ Скриншот получен! / Skrinshot qabul qilindi!\n\n"
        "⏳ Ожидайте подтверждения администратора.\n"
        "⏳ Admin tasdiqlashini kuting.\n"
        "Вам придёт уведомление / Sizga xabar keladi."
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}"),
        ]
    ]
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=(
            f"💰 Новый заказ!\n\n"
            f"👤 Покупатель: {user.full_name}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📎 @{user.username or 'нет'}\n\n"
            f"📦 Заказ: {order.get('type', '?')} — {order.get('item', '?')}\n"
            f"💵 Сумма: {order.get('price', '?')}\n"
            f"🎯 Отправить на: **{target}**\n\n"
            f"Подтвердить?"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ Только админ!", show_alert=True)
        return

    action, user_id = query.data.split("_", 1)
    user_id = int(user_id)

    if action == "approve":
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 Оплата подтверждена! / To'lov tasdiqlandi!\n\n"
                "🌟 Ваш заказ будет выполнен в ближайшее время.\n"
                "🌟 Buyurtmangiz tez orada bajariladi.\n"
                "Спасибо за покупку! / Xaridingiz uchun rahmat!"
            )
        )
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n✅ ПОДТВЕРЖДЕНО"
        )

    elif action == "reject":
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ Оплата не подтверждена. / To'lov tasdiqlanmadi.\n\n"
                "Возможно скриншот некорректный.\n"
                "Skrinshot noto'g'ri bo'lishi mumkin.\n"
                "Свяжитесь с поддержкой. / Yordam bilan bog'laning."
            )
        )
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n❌ ОТКЛОНЕНО"
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(admin_decision, pattern="^(approve|reject)_"))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
