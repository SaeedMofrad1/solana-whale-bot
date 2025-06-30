import asyncio
import json
import os
import re
import requests

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from keep_alive import keep_alive

# 🟢 ربات تلگرام
bot_token = "7915312006:AAGJ1gsx-40BEcVgZX3eBopBY7HhesLy5iA"

# 🟢 API کلید هیلیوس برای گرفتن دیتا از سولانا
helius_api_key = "42c9684f-2cd1-48ce-b05e-69722becc33b"

# 🟢 فقط آی‌دی تلگرام خودت برای کنترل ربات
allowed_user = "819727144"  # جایگزین با آیدی خودت

wallets_file = "wallets.json"

def load_wallets():
    if not os.path.exists(wallets_file):
        return []
    with open(wallets_file, "r") as f:
        return json.load(f)

def save_wallets(wallets):
    with open(wallets_file, "w") as f:
        json.dump(wallets, f, indent=4)

def get_token_info(mint_address):
    try:
        url = f"https://tokens.jup.ag/token/{mint_address}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != allowed_user:
        return
    await update.message.reply_text("✅ ربات فعال شد و آماده‌ست.")

# می‌تونی اینجا بقیه‌ی دستورات و مانیتور رو اضافه کنی

if __name__ == "__main__":
    keep_alive()  # روشن نگه داشتن سرور

    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))

    print("✅ Bot is running...")
    app.run_polling()
