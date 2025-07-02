"""
Redis Subscriber Module
Gestisce l'ascolto automatico dei messaggi dal channel Redis 'rss_feed'
"""

import redis
import threading
import json
import time
import os
import logging
import atexit
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class RedisSubscriber:
    """
    Redis Subscriber per gestire i messaggi dal channel rss_feed
    Avvio automatico in background
    """
    def __init__(self, redis_host='localhost', redis_port=6379, channel='rss_feed'):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.channel = channel
        self.redis_client = None
        self.pubsub = None
        self.running = False
        self.listener_thread = None
        self.message_handler = None
        
    def set_message_handler(self, handler):
        """Imposta la funzione per gestire i messaggi ricevuti"""
        self.message_handler = handler
        
    def connect(self):
        """Connessione a Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host, 
                port=self.redis_port, 
                decode_responses=True
            )
            # Test della connessione
            self.redis_client.ping()
            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe(self.channel)
            logger.info(f"Connesso a Redis {self.redis_host}:{self.redis_port}, channel: {self.channel}")
            return True
        except Exception as e:
            logger.error(f"Errore connessione Redis: {str(e)}")
            return False
    
    def start_listening(self):
        """Avvia l'ascolto dei messaggi in un thread separato"""
        if self.running:
            logger.info("Redis subscriber già in esecuzione")
            return True
            
        if not self.connect():
            return False
            
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen_for_messages, daemon=True)
        self.listener_thread.start()
        logger.info("Redis subscriber avviato automaticamente in background")
        return True
    
    def stop_listening(self):
        """Ferma l'ascolto dei messaggi"""
        if not self.running:
            return
            
        logger.info("Fermando Redis subscriber...")
        self.running = False
        
        if self.pubsub:
            try:
                self.pubsub.unsubscribe(self.channel)
                self.pubsub.close()
            except Exception as e:
                logger.error(f"Errore chiusura pubsub: {str(e)}")
                
        if self.redis_client:
            try:
                self.redis_client.close()
            except Exception as e:
                logger.error(f"Errore chiusura Redis client: {str(e)}")
                
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=5)
            
        logger.info("Redis subscriber fermato")
    
    def _listen_for_messages(self):
        """Loop principale per l'ascolto dei messaggi"""
        logger.info(f"Iniziato ascolto messaggi dal channel: {self.channel}")
        
        # Attende il messaggio di conferma sottoscrizione
        subscription_confirmed = False
        
        try:
            from langsmith.utils import ContextThreadPoolExecutor
            with ContextThreadPoolExecutor(max_workers=3) as executor:
                while self.running:
                    # Usa get_message() con timeout per non bloccare indefinitamente
                    message = self.pubsub.get_message(timeout=None)
                    
                    if message is None:
                        # Nessun messaggio ricevuto nel timeout, continua il loop
                        continue
                        
                    logger.info(f"Ricevuto messaggio: {message}")
                    
                    # Gestisce i messaggi veri del canale
                    if message['type'] == 'message':
                        try:
                            logger.info(f"Ricevuto messaggio dal canale: {message['channel']}")
                            # Decodifica il messaggio JSON
                            msg_data = json.loads(message['data'])
                            logger.info(f"Ricevuto messaggio: {msg_data.get('title', 'N/A')}")
                            
                            # Chiama il message handler se è stato impostato
                            if self.message_handler:
                                executor.submit(self.message_handler, msg_data)
                            else:
                                logger.warning("Nessun message handler configurato")
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Errore decodifica JSON del messaggio: {str(e)}")
                            logger.error(f"Messaggio raw: {message['data']}")
                        except Exception as e:
                            logger.error(f"Errore elaborazione messaggio: {str(e)}")
                            
                    # Gestisce altri tipi di messaggio per debug
                    elif message['type'] in ['unsubscribe', 'psubscribe', 'punsubscribe']:
                        logger.info(f"Messaggio di controllo: {message['type']} per {message.get('channel', 'N/A')}")
                    else:
                        logger.warning(f"Tipo di messaggio non gestito: {message['type']}")
                        
        except Exception as e:
            logger.error(f"Errore nel loop di ascolto Redis: {str(e)}")
        finally:
            logger.info("Loop di ascolto Redis terminato")
    


# Istanza globale del subscriber Redis
redis_subscriber = None

def init_redis_subscriber(message_handler=None):
    """
    Inizializza e avvia il subscriber Redis automaticamente
    
    Args:
        message_handler: Funzione per gestire i messaggi ricevuti
    """
    global redis_subscriber
    
    try:
        # Ottieni parametri Redis dalle variabili d'ambiente
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        logger.info(f"Inizializzazione Redis subscriber: {redis_host}:{redis_port}")
        
        # Crea il subscriber
        redis_subscriber = RedisSubscriber(
            redis_host=redis_host,
            redis_port=redis_port,
            channel='rss_feed'
        )
        
        # Imposta il message handler se fornito
        if message_handler:
            redis_subscriber.set_message_handler(message_handler)
        
        # Avvia l'ascolto in background
        if redis_subscriber.start_listening():
            logger.info("Redis subscriber inizializzato e avviato con successo")
            # Registra la funzione di cleanup per la chiusura dell'app
            atexit.register(cleanup_redis_subscriber)
            return True
        else:
            logger.error("Fallimento nell'avvio del Redis subscriber")
            return False
            
    except Exception as e:
        logger.error(f"Errore nell'inizializzazione del Redis subscriber: {str(e)}")
        return False

def cleanup_redis_subscriber():
    """Cleanup function chiamata alla chiusura dell'applicazione"""
    global redis_subscriber
    if redis_subscriber:
        redis_subscriber.stop_listening()
        redis_subscriber = None

def get_redis_subscriber():
    """Restituisce l'istanza del subscriber Redis"""
    return redis_subscriber

def test_redis_pubsub():
    """Funzione di test per verificare il funzionamento del pub/sub Redis"""
    global redis_subscriber
    
    if not redis_subscriber:
        logger.error("Redis subscriber non inizializzato. Chiamare prima init_redis_subscriber()")
        return False
        
    logger.info("=== Test Redis Pub/Sub ===")
    
    # Test connessione
    try:
        redis_subscriber.redis_client.ping()
        logger.info("✅ Connessione Redis OK")
    except Exception as e:
        logger.error(f"❌ Errore connessione Redis: {str(e)}")
        return False
    
    
    return True
