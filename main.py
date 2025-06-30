import asyncio
import json
import os
import re
import requests

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

bot_token = "7915312006:AAGJ1gsx-40BEcVgZX3eBopBY7HhesLy5iA"
helius_api_key = "42c9684f-2ec1-4a0c-b50e-69728eccc23b"
allowed_user = "819727144"
wallets_file = "wallets.json"

def load_wallets():
    if not os.path.exists(wallets_file):
        return []
    with open(wallets_file, "r") as f:
        return json.load(f)

def save_wallets(wallets):
    with open(wallets_file, "w") as f:
        json.dump(wallets, f, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != allowed_user:
        return
    await update.message.reply_text("✅ ربات فعال است.")

async def add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != allowed_user:
        return
    if len(context.args) != 1:
        await update.message.reply_text("آدرس ولت را به درستی وارد کنید.")
        return
    wallet = context.args[0]
    wallets = load_wallets()
    if wallet in wallets:
        await update.message.reply_text("این ولت قبلاً اضافه شده.")
        return
    wallets.append(wallet)
    save_wallets(wallets)
    await update.message.reply_text(f"✅ ولت {wallet} اضافه شد.")

async def remove_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != allowed_user:
        return
    if len(context.args) != 1:
        await update.message.reply_text("آدرس ولت را به درستی وارد کنید.")
        return
    wallet = context.args[0]
    wallets = load_wallets()
    if wallet not in wallets:
        await update.message.reply_text("این ولت در لیست نیست.")
        return
    wallets.remove(wallet)
    save_wallets(wallets)
    await update.message.reply_text(f"❌ ولت {wallet} حذف شد.")

async def list_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != allowed_user:
        return
    wallets = load_wallets()
    if not wallets:
        await update.message.reply_text("هیچ ولتی ثبت نشده.")
    else:
        msg = "📜 لیست ولت‌ها:\n" + "\n".join(wallets)
        await update.message.reply_text(msg)

def main():
    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_wallet))
    app.add_handler(CommandHandler("remove", remove_wallet))
    app.add_handler(CommandHandler("list", list_wallets))

    keep_alive()
    app.run_polling()

if __name__ == "__main__":
    main()
