import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ==============================
# 🔐 PUT YOUR TOKEN HERE
# ==============================
TOKEN = "8213049232:AAE8IbmriRtMpTY6xTg_R5CagmQ1dlsS160"

TENDER_API_URL = "https://tendersearchai.tendertiger.co.in/api/tender/GetTendersListBeforeLoginAI"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ==============================
# 📡 CALL API
# ==============================
def call_tender_api(keyword: str, total: int = 20):
    payload = {
        "searchkeyword": keyword,
        "total": total,
        "rescount": 0,
        "maxScore": 0,
        "Hosturl": "https://tendersearchai.tendertiger.co.in",
    }

    try:
        response = requests.post(TENDER_API_URL, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data.get("TenderList", [])
    except Exception as e:
        logger.error(f"API Error: {e}")
        return []


# ==============================
# 🤖 START
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Welcome to Tender Search Bot!\n\n"
        "Type any keyword to search tenders."
    )


# ==============================
# 🔍 SEARCH FUNCTION
# ==============================
async def send_tenders(update, context, keyword, start_index=0, count=5):

    tenders = call_tender_api(keyword, total=20)

    if not tenders:
        await update.message.reply_text("❌ No tenders found.")
        return

    end_index = start_index + count
    selected = tenders[start_index:end_index]

    if not selected:
        await update.message.reply_text("❌ No more tenders available.")
        return

    reply_text = f"📄 Tender Results for: {keyword}\n\n"

    for i, tender in enumerate(selected, start_index + 1):
        title = tender.get("tendersbriefnew", "No Title")
        ref_no = tender.get("tenderrefno", "N/A")
        state = tender.get("statename", "N/A")
        company = tender.get("companyname", "N/A")
        value = tender.get("tendervalue", "N/A")
        closing_date = tender.get("closingdate", "N/A")

        reply_text += (
            f"🔹 {i}. {title}\n"
            f"📌 Ref No: {ref_no}\n"
            f"🏢 Dept: {company}\n"
            f"📍 State: {state}\n"
            f"💰 Value: ₹{value}\n"
            f"📅 Closing: {closing_date}\n\n"
        )

    # Save current position
    context.user_data["keyword"] = keyword
    context.user_data["offset"] = end_index

    # Add button
    keyboard = [
        [InlineKeyboardButton("🔽 Show More", callback_data="show_more")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(reply_text[:4000], reply_markup=reply_markup)


# ==============================
# 🔎 SEARCH HANDLER
# ==============================
async def search_tenders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.message.text.strip().lower()

    # If user types "show more"
    if keyword in ["show more", "more", "give more"]:
        if "keyword" not in context.user_data:
            await update.message.reply_text("⚠️ Please search something first.")
            return

        await send_tenders(
            update,
            context,
            context.user_data["keyword"],
            start_index=context.user_data.get("offset", 0),
            count=3
        )
    else:
        await update.message.reply_text("🔎 Searching tenders...")
        await send_tenders(update, context, keyword, start_index=0, count=5)


# ==============================
# 🔘 BUTTON HANDLER
# ==============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "show_more":

        keyword = context.user_data.get("keyword")
        offset = context.user_data.get("offset", 0)

        if not keyword:
            await query.edit_message_text("⚠️ Please search first.")
            return

        tenders = call_tender_api(keyword, total=20)

        selected = tenders[offset:offset+3]

        if not selected:
            await query.edit_message_text("❌ No more tenders available.")
            return

        reply_text = ""

        for i, tender in enumerate(selected, offset + 1):
            title = tender.get("tendersbriefnew", "No Title")
            ref_no = tender.get("tenderrefno", "N/A")
            state = tender.get("statename", "N/A")
            company = tender.get("companyname", "N/A")
            value = tender.get("tendervalue", "N/A")
            closing_date = tender.get("closingdate", "N/A")

            reply_text += (
                f"🔹 {i}. {title}\n"
                f"📌 Ref No: {ref_no}\n"
                f"🏢 Dept: {company}\n"
                f"📍 State: {state}\n"
                f"💰 Value: ₹{value}\n"
                f"📅 Closing: {closing_date}\n\n"
            )

        context.user_data["offset"] = offset + 3

        await query.message.reply_text(reply_text[:4000])


# ==============================
# 🚀 MAIN
# ==============================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_tenders))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()