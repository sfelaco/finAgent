import os
import json
import requests
from typing import Any, Dict, cast
from graph.state import GraphState, NewsScore
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardMarkup
import asyncio

load_dotenv()

def telegram_notify(state: GraphState) -> Dict[str, Any]:
    print("---TELEGRAM NOTIFIER ---")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
    TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        raise ValueError("Telegram token o channel id non configurati!")
    if not state:
        raise ValueError("news_analysis (GraphState) è obbligatorio!")

    # Estrai i dati richiesti
    rss_title = state.get("rss_title")
    rss_link = state.get("rss_link")
    na = state.get("news_scoring")
    if not rss_title or not rss_link or not na:
        raise ValueError("rss_title, rss_link e news_analysis sono obbligatori in GraphState!")

    thread_id = state.get("thread_id", "unknown")
    
    # Crea i bottoni inline per ogni asset
    inline_keyboard = []
    for asset in na.assets:
        button = {
            "text": f"\U0001F4C8 {asset}",
            "callback_data": f"asset_analysis_{asset}_{thread_id}"
        }
        inline_keyboard.append([button])

    
    
    message = (
        f"\U0001F4F0 <b>News Alert</b>\n"
        f"<b>Title:</b> {rss_title}\n"
        f"<b>Link:</b> <a href='{rss_link}'>{rss_link}</a>\n\n"
        f"<b>Score:</b> {na.score}/5\n"
        f"<b>Assets:</b> {', '.join(na.assets)}\n"
        f"<b>Description:</b> {na.description}\n\n"
        f"\U0001F447 Clicca sui bottoni per analizzare gli asset"
    )
    
    async def _send():
        # Send to channel (no buttons)
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=message,
            parse_mode="HTML"
        )
        # Send to group (with buttons)
        if TELEGRAM_GROUP_ID:
            await bot.send_message(
                chat_id=TELEGRAM_GROUP_ID,
                text=message,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard)
            )

    # Send to channel using python-telegram-bot
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        asyncio.run(_send())
    except Exception as e:
        print(f"Telegram error: {e}")
    return {k: state[k] for k in state}


if __name__ == "__main__":
    
    
    news_analysis = NewsScore(
        assets=["SPY", "USO"],
        score = 4,
        description="Global stocks fell and oil futures rose on a report that the U.S. may soon strike Iran, raising concerns about a potential conflict in the Middle East.",)

    state = {
        "rss_title": "U.S. Stocks Fall, Oil Rises on Iran Tensions",
        "rss_link": "https://example.com/news/iran-tensions",
        "news_scoring": news_analysis,
        "thread_id": 12345,
        "documents": None, 
        "answer_language": "italian", 
        "analysis_path": "" 
    }
    # Act
    result = telegram_notify(cast(GraphState, state))
    print(result)