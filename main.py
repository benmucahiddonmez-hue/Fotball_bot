from flask import Flask
import os
import threading
import requests
import telebot
from datetime import datetime

# Telegram Bot Token
TELEGRAM_TOKEN = '8575255003:AAGp9pQqRcOnJNnS4BJ6TiB536-idtXw7JI'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Flask Web Sunucusu
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot aktif ve calisiyor!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Flask'ı arka planda başlatıyoruz
threading.Thread(target=run_flask, daemon=True).start()

def fetch_sofascore_data():
    today_str = datetime.now().strftime('%Y-%m-%d')
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{today_str}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.sofascore.com/',
        'Origin': 'https://www.sofascore.com'
    }
    
    try:
        print(f"Sofascore'dan {today_str} tarihi için veri isteniyor...")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Durum kodu: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            print(f"Gelen toplam maç sayısı: {len(events)}")
            return data
    except Exception as e:
        print(f"Hata oluştu: {e}")
    return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "⚽ *Futbol Botuna Hoş Geldiniz!*\n\n"
        "📌 *Komutlar:*\n"
        "• `/maclar` — Günün maç bülteni\n"
        "• `/canli` — Anlık canlı maçlar\n"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['maclar'])
def get_all_matches(message):
    msg = bot.reply_to(message, "⏳ Bülten Sofascore'dan çekiliyor...")
    try:
        data = fetch_sofascore_data()
        if not data or 'events' not in data or not data['events']:
            bot.edit_message_text("❌ Bugün için bülten bulunamadı.", chat_id=msg.chat.id, message_id=msg.message_id)
            return

        events = data['events']
        text = "⚽ *GÜNÜN MAÇ BÜLTENİ*\n\n"
        count = 0
        
        for ev in events[:15]:
            home = ev.get('homeTeam', {}).get('name', 'Ev')
            away = ev.get('awayTeam', {}).get('name', 'Dep')
            tournament = ev.get('tournament', {}).get('name', 'Lig')
            
            startTimestamp = ev.get('startTimestamp', 0)
            if startTimestamp:
                time_str = datetime.fromtimestamp(startTimestamp).strftime('%H:%M')
            else:
                time_str = ""
                
            text += f"🏆 *{tournament}*\n• {home} vs {away} (⏰ {time_str})\n\n"
            count += 1

        if count == 0:
            text = "📅 Bugün maç bulunamadı."

        bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ Hata: {e}", chat_id=msg.chat.id, message_id=msg.message_id)

@bot.message_handler(commands=['canli'])
def get_live_matches(message):
    msg = bot.reply_to(message, "⏳ Canlı maçlar kontrol ediliyor...")
    try:
        data = fetch_sofascore_data()
        if not data or 'events' not in data:
            bot.edit_message_text("🔴 Şu anda canlı maç verisi alınamadı.", chat_id=msg.chat.id, message_id=msg.message_id)
            return

        live_matches = []
        for ev in data['events']:
            status_type = ev.get('status', {}).get('type', '')
            if status_type == 'inprogress':
                home = ev.get('homeTeam', {}).get('name', '')
                away = ev.get('awayTeam', {}).get('name', '')
                home_score = ev.get('homeScore', {}).get('current', '0')
                away_score = ev.get('awayScore', {}).get('current', '0')
                status_desc = ev.get('status', {}).get('description', 'Canlı')
                
                live_matches.append(f"⚡ *{home}* {home_score} - {away_score} *{away}* ({status_desc})")

        if not live_matches:
            bot.edit_message_text("🔴 Şu anda canlı oynanan maç bulunmuyor.", chat_id=msg.chat.id, message_id=msg.message_id)
            return

        text = "🔴 *CANLI MAÇLAR*\n\n" + "\n".join(live_matches[:10])
        bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ Hata: {e}", chat_id=msg.chat.id, message_id=msg.message_id)

if __name__ == "__main__":
    print("Bot ve Sofascore Entegrasyonu Başlatıldı!")
    bot.infinity_polling(none_stop=True, interval=0, timeout=20)
