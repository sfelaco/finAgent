from graph.graph import create_graph
from dotenv import load_dotenv
import os
import redis
import time
import json
import concurrent.futures
import asyncio
from langsmith import trace

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_QUEUE = os.getenv('REDIS_QUEUE', 'rss_feed')
import threading
from langsmith import traceable
from langsmith.utils import ContextThreadPoolExecutor




if __name__ == "__main__":
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    print("In attesa di messaggi dalla coda Redis...")
    app = create_graph()
    loop = asyncio.get_event_loop()
    
    @traceable(name="invoke_graph")
    def process_message(msg):
        try:
            print(f"Elaborazione del messaggio: {msg['title']}")
            thread_id = threading.get_ident()
            config = {"configurable": {"thread_id": thread_id}}
            # Crea un nuovo event loop per ogni thread
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            coro = app.ainvoke(input={
                "rss_title": msg['title'],
                "rss_link": msg['link'],
                "answer_language": "italian",
                "thread_id": thread_id
            }, config=config)
            response = new_loop.run_until_complete(coro)
            new_loop.close()
        except Exception as e:
            print(f"Errore durante l'elaborazione del messaggio: {e}")

   
    with ContextThreadPoolExecutor(max_workers=3) as executor:
        while True:
            try:
                msg = r.brpop(REDIS_QUEUE, timeout=0)
                if msg:
                    msg_dict = json.loads(msg[1])
                    executor.submit(process_message, msg_dict)
            except Exception as e:
                print(f"Errore: {e}")

