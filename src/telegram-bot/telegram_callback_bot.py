import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv


load_dotenv()
# Assicurati di avere il token del bot nelle variabili d'ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        print("Not a callback query, do nothing")
        return

    user_id = query.from_user.id
    await query.answer()
    try:
        await context.bot.send_message(chat_id=user_id, text="CIAO")
    except Exception as e:
        print(f"Non posso inviare messaggio privato a {user_id}: {e}")

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN non impostato nelle variabili d'ambiente!")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(button_callback))
    print("Bot in ascolto... Clicca un pulsante inline per testare.")
    app.run_polling()

"""
Esempio di test:
1. Avvia questo script: python telegram_callback_bot.py
2. Invia un messaggio con pulsanti inline (ad esempio tramite la funzione telegram_notify già implementata).
3. Clicca su uno dei pulsanti dal tuo account Telegram.
4. Se hai già avviato una chat privata con il bot, riceverai un messaggio "CIAO" in privato.
""" 