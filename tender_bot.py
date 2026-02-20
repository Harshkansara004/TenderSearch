import requests
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==============================
# 🔐 PUT YOUR NEW TOKEN HERE
# ==============================
TOKEN = "8405024974:AAF4xG7ehZT7bdLzNebYepOFb1G-Jn4vBfA"

TENDER_API_URL = "https://tendersearchai.tendertiger.co.in/api/tender/GetTendersListBeforeLoginAI"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


# ==============================
# 📡 CALL TENDER API
# ==============================
def call_tender_api(keyword: str, total: int = 5) -> list:
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

        # Try possible response formats
        if isinstance(data, list):
            return data

        if "data" in data:
            return data["data"]

        if "result" in data:
            return data["result"]

        return []

    except Exception as e:
        logging.error(f"API Error: {e}")
        return []


# ==============================
# 🤖 START COMMAND
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Welcome to Tender Search Bot!\n\n"
        "Type any keyword to search tenders.\n\n"
        "Example:\nroad\nsolar\nconstruction"
    )


# ==============================
# 🔍 SEARCH FUNCTION
# ==============================
async def search_tenders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.message.text.strip()

    if not keyword:
        return

    await update.message.reply_text("🔎 Searching tenders... Please wait.")

    tenders = call_tender_api(keyword, total=5)

    if not tenders:
        await update.message.reply_text("❌ No tenders found.")
        return

    reply_text = f"📄 Tender Results for: {keyword}\n\n"

    for i, tender in enumerate(tenders[:5], 1):
        title = str(tender.get("title") or tender.get("workDesc") or "No Title")
        ref_no = str(tender.get("refNo") or tender.get("tenderNo") or "N/A")
        due_date = str(tender.get("dueDate") or tender.get("closingDate") or "N/A")

        reply_text += (
            f"{i}. {title}\n"
            f"Ref No: {ref_no}\n"
            f"Due Date: {due_date}\n\n"
        )

    # Telegram message limit protection
    if len(reply_text) > 4000:
        reply_text = reply_text[:4000]

    await update.message.reply_text(reply_text)


# ==============================
# 🚀 MAIN FUNCTION
# ==============================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_tenders))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()