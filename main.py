import asyncio
import json
import os
import re
import requests

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from keep_alive import keep_alive  # اگه استفاده نمی‌کنی می‌تونی حذفش کنی

bot_token = "7915312006:AAGJ1gsx-40BEcVgZX3eBopBY7HhesLy5iA"
helius_api_key = os.getenv("42c9684f-2ec1-4a0c-b50e-69728eccc23b") or "کلید_هیلیوس_تو"  # جایگزین کن اگر خواستی
allowed_user = os.getenv("ALLOWED_USER", "819727144")  # آیدی عددی خودت
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
        url = f"https://tokens.jupiterapi.com/tokens/{mint_address}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != allowed_user:
        return
    await update.message.reply_text("ربات فعال است ✅")

async def add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != allowed_user:
        return
    if len(context.args) != 1:
        await update.message.reply_text("فرمت اشتباه است. استفاده از: /add <wallet_address>")
        return
    wallet = context.args[0]
    wallets = load_wallets()
    if wallet in wallets:
        await update.message.reply_text("این والت قبلاً اضافه شده.")
        return
    wallets.append(wallet)
    save_wallets(wallets)
    await update.message.reply_text("والت با موفقیت اضافه شد.")

async def list_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != allowed_user:
        return
    wallets = load_wallets()
    if not wallets:
        await update.message.reply_text("هیچ والتی اضافه نشده.")
        return
    await update.message.reply_text("\n".join(wallets))

async def remove_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != allowed_user:
        return
    if len(context.args) != 1:
        await update.message.reply_text("فرمت اشتباه است. استفاده از: /remove <wallet_address>")
        return
    wallet = context.args[0]
    wallets = load_wallets()
    if wallet not in wallets:
        await update.message.reply_text("این والت وجود ندارد.")
        return
    wallets.remove(wallet)
    save_wallets(wallets)
    await update.message.reply_text("والت حذف شد.")

async def main():
    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_wallet))
    app.add_handler(CommandHandler("remove", remove_wallet))
    app.add_handler(CommandHandler("list", list_wallets))
    keep_alive()  # اگه نیاز نداری، حذفش کن
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
