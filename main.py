import asyncio
import json
import os
import re
import requests

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ثابت‌ها
BOT_TOKEN = "7915312006:AAGJ1gsx-40BEcVgZX3eBopBY7HhesLy5iA"
ALLOWED_USER = 819772214  # آیدی عددی خودت
WALLETS_FILE = "wallets.json"

# لود کردن لیست والت‌ها
def load_wallets():
    if not os.path.exists(WALLETS_FILE):
        return []
    with open(WALLETS_FILE, "r") as f:
        return json.load(f)

# ذخیره‌سازی والت‌ها
def save_wallets(wallets):
    with open(WALLETS_FILE, "w") as f:
        json.dump(wallets, f, indent=4)

# دستور استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER:
        return
    await update.message.reply_text("سلام! ربات فعال است ✅")

# افزودن والت جدید
async def add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER:
        return
    if not context.args:
        await update.message.reply_text("لطفاً آدرس والت را وارد کن.")
        return
    new_wallet = context.args[0]
    wallets = load_wallets()
    if new_wallet in wallets:
        await update.message.reply_text("این والت قبلاً اضافه شده.")
        return
    wallets.append(new_wallet)
    save_wallets(wallets)
    await update.message.reply_text("✅ والت با موفقیت اضافه شد.")

# حذف والت
async def remove_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER:
        return
    if not context.args:
        await update.message.reply_text("آدرس والت مورد نظر برای حذف را وارد کن.")
        return
    wallet = context.args[0]
    wallets = load_wallets()
    if wallet not in wallets:
        await update.message.reply_text("این والت در لیست نیست.")
        return
    wallets.remove(wallet)
    save_wallets(wallets)
    await update.message.reply_text("❌ والت حذف شد.")

# نمایش لیست والت‌ها
async def list_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER:
        return
    wallets = load_wallets()
    if not wallets:
        await update.message.reply_text("لیست والت‌ها خالیه.")
        return
    msg = "لیست والت‌ها:\n" + "\n".join(wallets)
    await update.message.reply_text(msg)

# شروع ربات
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_wallet))
    app.add_handler(CommandHandler("remove", remove_wallet))
    app.add_handler(CommandHandler("list", list_wallets))
    print("✅ ربات آماده است...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
