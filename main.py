from flask import Flask
import os
import threading
import requests
import telebot
from datetime import datetime

# Telegram Bot Token
TELEGRAM_TOKEN = '8575255003:AAGp9pQqRcOnJNnS4BJ6TiB536-idtXw7JI'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Flask Web Sunucusu (Render port hatasını önlemek için)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot aktif ve calisiyor!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Flask'ı arka planda başlatıyoruz
threading.Thread(target=run_flask, daemon=True).start()

def fetch_open_matches():
    # Engelsiz ve açık topluluk verisi / statik JSON kaynağı
    url = "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/en.1.json"
    
    try:
        print("Engelsiz açık kaynak bülteni isteniyor...")
        response = requests.get(url, timeout=10)
        print(f"Durum kodu: {response.status_code}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Hata oluştu: {e}")
    return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "⚽ *Futbol Botuna Hoş Geldiniz!*\n\n"
        "📌 *Komutlar:*\n"
        "• `/maclar` — Maç bülteni\n"
        "• `/canli` — Anlık durum\n"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['maclar'])
def get_all_matches(message):
    msg = bot.reply_to(message, "⏳ Bülten yükleniyor...")
    try:
        data = fetch_open_matches()
        if not data or 'matches' not in data:
            bot.edit_message_text("❌ Bülten verisine ulaşılamadı.", chat_id=msg.chat.id, message_id=msg.message_id)
            return

        matches = data['matches']
        text = "⚽ *MAÇ BÜLTENİ*\n\n"
        count = 0
        
        for m in matches[:10]:
            home = m.get('team1', 'Ev')
            away = m.get('team2', 'Dep')
            date_str = m.get('date', '')
            text += f"• {home} vs {away} (📅 {date_str})\n"
            count += 1

        if count == 0:
            text = "📅 Maç bulunamadı."

        bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ Hata: {e}", chat_id=msg.chat.id, message_id=msg.message_id)

@bot.message_handler(commands=['canli'])
def get_live_matches(message):
    bot.reply_to(message, "🔴 Şu anda canlı maç verisi aktif değil, ancak bülten sistemi sorunsuz çalışıyor.")

if __name__ == "__main__":
    print("Bot ve Engelsiz Sunucu Başlatıldı!")
    bot.infinity_polling(none_stop=True, interval=0, timeout=20)
