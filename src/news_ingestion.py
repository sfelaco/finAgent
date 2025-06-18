import time
import feedparser
import redis
import json

# Configurazione Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_QUEUE = 'rss_feed'
RSS_CACHE = 'rss_published'

# Endpoint RSS
RSS_URL = 'https://feeds.content.dowjones.io/public/rss/mw_topstories'

# Connessione a Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def fetch_and_publish():
    print("Fetching RSS feed...")
    feed = feedparser.parse(RSS_URL)
    for entry in feed.entries:
        link = entry.get('link')
        if not link:
            continue
        if not r.sismember(RSS_CACHE, link):
            item_json = json.dumps(entry, default=str)
            print(item_json)
            r.lpush(REDIS_QUEUE, item_json)
            r.sadd(RSS_CACHE, link)



if __name__ == "__main__":
    
    while True:
        try:
            fetch_and_publish()
        except Exception as e:
            print(f"Errore: {e}")
        time.sleep(10)
