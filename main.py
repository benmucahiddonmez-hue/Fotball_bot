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

def fetch_super_lig_matches():
    # openfootball deposunun güncel 2026-27 sezonu Süper Lig (Türkiye) JSON adresi
    url = "https://raw.githubusercontent.com/openfootball/football.json/master/2026-27/tr.1.json"
    
    try:
        print("Güncel Süper Lig bülteni isteniyor...")
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
        "⚽ *Süper Lig & Futbol Botuna Hoş Geldiniz!*\n\n"
        "📌 *Komutlar:*\n"
        "• `/maclar` — Güncel Süper Lig Bülteni\n"
        "• `/canli` — Anlık durum\n"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['maclar'])
def get_all_matches(message):
    msg = bot.reply_to(message, "⏳ Güncel Süper Lig bülteni yükleniyor...")
    try:
        data = fetch_super_lig_matches()
        if not data or 'matches' not in data:
            bot.edit_message_text("❌ Bülten verisine ulaşılamadı.", chat_id=msg.chat.id, message_id=msg.message_id)
            return

        matches = data['matches']
        text = "🇹🇷 *SÜPER LİG GÜNCEL BÜLTEN*\n\n"
        count = 0
        
        # Bugünün tarihini alıp bugüne yakın veya güncel maçları gösterelim
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        for m in matches:
            match_date = m.get('date', '')
            home = m.get('team1', 'Ev')
            away = m.get('team2', 'Dep')
            
            # Güncel ve gelecekteki maçları veya genel akışı listeleyelim
            text += f"• {match_date} | {home} vs {away}\n"
            count += 1
            if count >= 15:  # Telegram mesaj sınırına takılmamak için ilk 15 maç
                break

        if count == 0:
            text = "📅 Gösterilecek maç bulunamadı."

        bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ Hata: {e}", chat_id=msg.chat.id, message_id=msg.message_id)

@bot.message_handler(commands=['canli'])
def get_live_matches(message):
    bot.reply_to(message, "🔴 Güncel statik bülten üzerinden anlık canlı skorlar takip edilmektedir. Maç saatlerinde bülteni kontrol edebilirsiniz.")

if __name__ == "__main__":
    print("Bot ve Güncel Süper Lig Sunucusu Başlatıldı!")
    bot.infinity_polling(none_stop=True, interval=0, timeout=20)
