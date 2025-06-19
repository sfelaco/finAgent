import os
import requests
from typing import Any, Dict
from graph.state import GraphState, NewsAnalysis
from dotenv import load_dotenv

load_dotenv()

def telegram_notify(news_analysis: GraphState) -> Dict[str, Any]:
    print("---TELEGRAM NOTIFIER ---")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        raise ValueError("Telegram token o channel id non configurati!")
    if not news_analysis:
        raise ValueError("news_analysis (GraphState) è obbligatorio!")

    # Estrai i dati richiesti
    rss_title = news_analysis.get("rss_title")
    rss_link = news_analysis.get("rss_link")
    na = news_analysis.get("news_analysis")
    if not rss_title or not rss_link or not na:
        raise ValueError("rss_title, rss_link e news_analysis sono obbligatori in GraphState!")

    message = (
        f"\U0001F4F0 <b>News Alert</b>\n"
        f"<b>Title:</b> {rss_title}\n"
        f"<b>Link:</b> <a href='{rss_link}'>{rss_link}</a>\n\n"
        f"<b>Score:</b> {na.score}/5\n"
        f"<b>Assets:</b> {', '.join(na.assets)}\n"
        f"<b>Description:</b> {na.description}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code != 200:
            print(f"Telegram error: {resp.text}")
    except Exception as e:
        print(f"Internal error: {e}")
    return {}


if __name__ == "__main__":
    
    
    news_analysis = NewsAnalysis(
        assets=["SPY", "USO"],
        score = 4,
        description="Global stocks fell and oil futures rose on a report that the U.S. may soon strike Iran, raising concerns about a potential conflict in the Middle East.",)

    state = GraphState(
        rss_title="U.S. Stocks Fall, Oil Rises on Iran Tensions",
        rss_link="https://example.com/news/iran-tensions",
        news_analysis=news_analysis
    )
    # Act
    result = telegram_notify(state)
    print(result)