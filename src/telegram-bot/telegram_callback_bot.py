import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, MessageHandler, filters, ChatMemberHandler
from dotenv import load_dotenv


load_dotenv()
# Assicurati di avere il token del bot nelle variabili d'ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = int(os.getenv("TELEGRAM_GROUP_ID", "0"))
TELEGRAM_CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID", "0"))

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

def extract_status_change(chat_member_update):
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))
    if status_change is None:
        return None
    old_status, new_status = status_change
    was_member = old_status in [
        "member", "administrator", "owner"
    ] or (old_status == "restricted" and old_is_member is True)
    is_member = new_status in [
        "member", "administrator", "owner"
    ] or (new_status == "restricted" and new_is_member is True)
    return was_member, is_member

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("New user joined")
    if update.message and update.message.new_chat_members and update.effective_chat:
        for member in update.message.new_chat_members:
            member_name = f"{member.first_name} {member.last_name}" 
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"""Benvenuto {member_name} su FinAgent group, qui troverai le ultime news finanziarie con una breve analisi, clicca su @finagentbot_bot e clicca su /start per ricevere le analisi approfondite degli asset."""
            )

async def check_group_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.my_chat_member:
        chat = update.my_chat_member.chat
        adder = update.my_chat_member.from_user
        allowed_ids = [TELEGRAM_GROUP_ID, TELEGRAM_CHANNEL_ID]
        if chat.id not in allowed_ids:
            print(f"[SECURITY] Il bot è stato aggiunto senza permesso da {adder.full_name} (id: {adder.id}) nel gruppo/canale '{chat.title}' (id: {chat.id})")
            try:
                await context.bot.leave_chat(chat_id=chat.id)
                print(f"Il bot ha lasciato il gruppo/canale non autorizzato: {chat.title} (id: {chat.id})")
            except Exception as e:
                print(f"Errore nell'uscita dal gruppo/canale non autorizzato: {e}")

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN non impostato nelle variabili d'ambiente!")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(ChatMemberHandler(check_group_channel, ChatMemberHandler.MY_CHAT_MEMBER))
    print("Bot in ascolto... Clicca un pulsante inline per testare.")
    app.run_polling()

"""
Esempio di test:
1. Avvia questo script: python telegram_callback_bot.py
2. Invia un messaggio con pulsanti inline (ad esempio tramite la funzione telegram_notify già implementata).
3. Clicca su uno dei pulsanti dal tuo account Telegram.
4. Se hai già avviato una chat privata con il bot, riceverai un messaggio "CIAO" in privato.
""" 