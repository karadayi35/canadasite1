from flask import Flask, jsonify
from flask_cors import CORS
from telethon import TelegramClient, events
import asyncio
import threading
import time
import re
import random

# Flask uygulaması
app = Flask(__name__)
CORS(app)

# Telegram API Bilgileri
api_id = '21745249'
api_hash = '89cf10c8782c9c54b671fc5736ddcf3b'
session_name = 'user_session'
group_id = -1001216775179  # Hedef grup ID'si

# İkon listesi
ICON_LIST = [
    "/public/icons/icon1.png",
    "/public/icons/icon2.png",
    "/public/icons/icon3.png",
    "/public/icons/icon4.png",
    "/public/icons/icon5.png",
    "/public/icons/icon6.png",
]

# Bot bilgileri
BOTS = [
    {"name": "Academybot", "icon": "/public/moderator.png", "message": "Telegram group: <a href='https://t.me/rouletteacademycanada'>Click</a>"},
    {"name": "StakeBot", "icon": "/public/slotticabot.png", "message": "Best Casino Go: <a href='https://stake.com/?c=9dd9dbc553'>Click</a>"},
    {"name": "Slotticabot", "icon": "/public/slotticabot.png", "message": "Best Casino Go: <a href='https://gopartner.link/?a=205678&c=184089&s1=6028'>Click</a>"},
    {"name": "BetsioBot", "icon": "/public/slotticabot.png", "message": "Best Casino Go: <a href='https://t.ly/9-D_G'>Click</a>"},
]

# Mesajları saklamak için listeler
messages = []
filtered_messages = []
bot_messages = []

@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify({"message": "Flask backend çalışıyor!"})

@app.route("/get_messages", methods=["GET"])
def get_messages():
    """Kullanıcı ve bot mesajlarını döndür."""
    global filtered_messages, bot_messages
    all_messages = filtered_messages + bot_messages
    filtered_messages = []  # Listeyi temizle
    bot_messages = []  # Listeyi temizle
    return jsonify(all_messages)

def is_valid_message(message_text):
    """Geçerli bir mesaj mı kontrol et."""
    if re.search(r'(https?://|t\.me)', message_text):
        return False
    return True

async def fetch_messages():
    """Telegram'dan mesajları sürekli çeken fonksiyon."""
    global messages
    async with TelegramClient(session_name, api_id, api_hash) as client:
        print("Telegram'a bağlanıldı!")

        @client.on(events.NewMessage(chats=group_id))
        async def handler(event):
            sender = await event.get_sender()
            username = sender.username or sender.first_name or "Anonim"
            message_text = event.message.text

            if not is_valid_message(message_text):
                print(f"Geçersiz mesaj atlandı: {message_text}")
                return

            # Rastgele ikon ata
            icon = random.choice(ICON_LIST)
            new_message = {"author": username, "content": message_text, "icon": icon}
            messages.append(new_message)
            print(f"Yeni mesaj alındı: {username} - {message_text}")

        await client.run_until_disconnected()

def process_messages():
    """Mesajları işleyip filtrelenmiş mesajlara ekleyen fonksiyon."""
    global messages, filtered_messages
    while True:
        if messages:
            message = messages.pop(0)
            filtered_messages.append(message)
            print(f"Mesaj işlendi: {message['content']}")
        time.sleep(3)  # Her mesaj arasında 3 saniye bekle

def schedule_bot_messages():
    """Bot mesajlarını düzenli olarak ekleyen fonksiyon."""
    global bot_messages
    while True:
        for bot in BOTS:
            bot_messages.append({
                "author": bot["name"],
                "content": bot["message"],
                "icon": bot["icon"]
            })
        time.sleep(60)  # Her 60 saniyede bir bot mesajları eklenir

def start_fetching():
    """Telegram mesajlarını çekmeyi başlat."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_messages())

if __name__ == "__main__":
    # Telegram mesajlarını çeken thread
    telegram_thread = threading.Thread(target=start_fetching)
    telegram_thread.daemon = True
    telegram_thread.start()

    # Kullanıcı mesajlarını işleyen thread
    process_thread = threading.Thread(target=process_messages)
    process_thread.daemon = True
    process_thread.start()

    # Bot mesajlarını planlayan thread
    bot_thread = threading.Thread(target=schedule_bot_messages)
    bot_thread.daemon = True
    bot_thread.start()

    # Flask API'yi başlat
    app.run(host="0.0.0.0", port=5000)
