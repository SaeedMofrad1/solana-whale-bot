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

bot_token = os.getenv("BOT_TOKEN")
helius_api_key = os.getenv("HELIUS_API_KEY")
allowed_user = int(os.getenv("ALLOWED_USER", "123456789"))
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
            token_data = response.json()
            return {
                "name": token_data.get("name", "Unknown"),
                "symbol": token_data.get("symbol", "???"),
                "decimals": token_data.get("decimals", 9)
            }
    except:
        pass

    try:
        url = f"https://api.helius.xyz/v0/token-metadata?api-key={helius_api_key}"
        payload = {"mintAccounts": [mint_address]}
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                token = data[0]
                return {
                    "name": token.get("onChainMetadata", {}).get("metadata", {}).get("name", "Unknown"),
                    "symbol": token.get("onChainMetadata", {}).get("metadata", {}).get("symbol", "???"),
                    "decimals": token.get("mint", {}).get("decimals", 9)
                }
    except:
        pass
    return {"name": "Unknown Token", "symbol": "???", "decimals": 9}

def format_amount(amount, decimals):
    try:
        amount = int(amount) if isinstance(amount, str) else amount
        formatted = amount / (10 ** decimals)
        if formatted >= 1e6:
            return f"{formatted/1e6:.2f}M"
        elif formatted >= 1e3:
            return f"{formatted/1e3:.2f}K"
        else:
            return f"{formatted:.4f}".rstrip('0').rstrip('.')
    except:
        return str(amount)

def analyze_transaction(tx, wallet_address):
    token_transfers = tx.get("tokenTransfers", [])
    results = []

    for transfer in token_transfers:
        mint = transfer.get("mint")
        amount = transfer.get("tokenAmount", 0)
        from_addr = transfer.get("fromUserAccount", "")
        to_addr = transfer.get("toUserAccount", "")

        if not mint or mint == "So11111111111111111111111111111111111111112":
            continue

        if from_addr == wallet_address:
            action = "🔴 فروش"
        elif to_addr == wallet_address:
            action = "🟢 خرید"
        else:
            continue

        token_info = get_token_info(mint)
        formatted_amount = format_amount(amount, token_info["decimals"])

        results.append({
            "action": action,
            "token_name": token_info["name"],
            "token_symbol": token_info["symbol"],
            "amount": formatted_amount,
            "mint": mint
        })

    return results

async def addwallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != allowed_user:
        await update.message.reply_text("⛔️ دسترسی غیرمجاز.")
        return

    if not context.args:
        await update.message.reply_text("❌ لطفاً آدرس ولت را وارد کن:\n/addwallet <آدرس>")
        return

    wallet = context.args[0].strip().strip("<>").strip()

    if not (32 <= len(wallet) <= 44):
        await update.message.reply_text("❌ آدرس نامعتبر است (طول اشتباه).")
        return
    if not re.match(r"^[A-HJ-NP-Za-km-z1-9]+$", wallet):
        await update.message.reply_text("❌ آدرس شامل کاراکتر نامعتبر است.")
        return

    wallets = load_wallets()
    if wallet in wallets:
        await update.message.reply_text("⚠️ این ولت قبلاً ثبت شده.")
    else:
        wallets.append(wallet)
        save_wallets(wallets)
        await update.message.reply_text(f"✅ ولت ثبت شد: `{wallet}`", parse_mode="Markdown")

async def removewallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != allowed_user:
        return
    if not context.args:
        await update.message.reply_text("❌ آدرس رو وارد کن:\n/removewallet <آدرس>")
        return
    wallet = context.args[0].strip()
    wallets = load_wallets()
    if wallet in wallets:
        wallets.remove(wallet)
        save_wallets(wallets)
        await update.message.reply_text(f"🗑 {wallet} حذف شد.")
    else:
        await update.message.reply_text("❌ ولت یافت نشد.")

async def listwallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != allowed_user:
        return
    wallets = load_wallets()
    if not wallets:
        await update.message.reply_text("📭 لیست ولت‌ها خالیه.")
    else:
        msg = "\n".join([f"• {w}" for w in wallets])
        await update.message.reply_text(f"📋 لیست ولت‌های ثبت شده:\n{msg}")

async def check_transactions(app: Application):
    seen_tx = {}
    print("🔍 در حال بررسی تراکنش‌ها...")

    while True:
        wallets = load_wallets()
        for wallet in wallets:
            try:
                url = f"https://api.helius.xyz/v0/addresses/{wallet}/transactions?api-key={helius_api_key}&limit=3"
                response = requests.get(url, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    for tx in data:
                        sig = tx.get("signature")
                        key = f"{wallet}_{sig}"
                        if key in seen_tx:
                            continue
                        seen_tx[key] = True

                        transactions = analyze_transaction(tx, wallet)

                        for trans in transactions:
                            msg = f"""🐋 **نهنگ رصد شد!**

{trans['action']} توسط: `{wallet[:6]}...{wallet[-4:]}`

🪙 **توکن:** {trans['token_name']} ({trans['token_symbol']})
💰 **مقدار:** {trans['amount']}
🔗 [Solscan](https://solscan.io/tx/{sig})

📊 **Contract:** `{trans['mint']}`"""

                            await app.bot.send_message(
                                chat_id=allowed_user,
                                text=msg,
                                parse_mode="Markdown",
                                disable_web_page_preview=True
                            )
                            print(f"📩 ارسال شد: {trans['action']} {trans['token_symbol']}")
                else:
                    print(f"❌ API Error {response.status_code}")
            except Exception as e:
                print(f"⚠️ خطا: {e}")
        await asyncio.sleep(30)

async def main():
    print("🤖 ربات راه‌اندازی شد...")
    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("addwallet", addwallet, block=False))
    app.add_handler(CommandHandler("removewallet", removewallet, block=False))
    app.add_handler(CommandHandler("listwallets", listwallets, block=False))

    asyncio.create_task(check_transactions(app))
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    keep_alive()
    asyncio.get_event_loop().run_until_complete(main())
