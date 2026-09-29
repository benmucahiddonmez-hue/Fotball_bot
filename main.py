from flask import Flask
import os
import threading
import requests
import telebot
from datetime import datetime, timedelta

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

# Desteklenen Ligler ve ESPN Kodları (Dünya Kupası eklendi)
LEAGUES = {
    "🇹🇷 Süper Lig": "tur.1",
    "🇬🇧 Premier League": "eng.1",
    "🇩🇪 Bundesliga": "ger.1",
    "🇮🇹 Serie A": "ita.1",
    "🇪🇸 La Liga": "esp.1",
    "🏆 Dünya Kupası / Milli": "fifa.world"
}

def fetch_scoreboard(slug):
    # Bugün ile önümüzdeki 7 günü kapsayan tarih aralığı (YYYYMMDD-YYYYMMDD)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    date_range = f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
    
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard?dates={date_range}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Hata ({slug}): {e}")
    return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "⚽ *Futbol & Dünya Kupası Botu*\n\n"
        "📌 *Komutlar:*\n"
        "• `/maclar` — Önümüzdeki 7 Günün Maçları\n"
        "• `/canli` — Anlık Canlı Skorlar\n"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['maclar'])
def get_all_matches(message):
    msg = bot.reply_to(message, "⏳ Önümüzdeki 7 günün bülteni taranıyor...")
    try:
        full_text = "⚽ *ÖNÜMÜZDEKİ 7 GÜNÜN MAÇLARI*\n\n"
        total_matches = 0

        for league_name, slug in LEAGUES.items():
            data = fetch_scoreboard(slug)
            if not data or 'events' not in data or not data['events']:
                continue

            full_text += f"*{league_name}*\n"
            league_count = 0

            for ev in data['events'][:6]: # Her ligden en fazla 6 maç
                status = ev.get('status', {}).get('type', {}).get('description', 'Planlandı')
                competitions = ev.get('competitions', [{}])[0]
                competitors = competitions.get('competitors', [])
                
                # Tarih/Saat bilgisi
                date_str = ev.get('date', '')
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%MZ")
                    time_formatted = (dt + timedelta(hours=3)).strftime('%d.%m %H:%M') # Türkiye saati (+3)
                except:
                    time_formatted = ""

                home_team, away_team, home_score, away_score = "Ev", "Dep", "0", "0"
                for comp in competitors:
                    if comp.get('homeAway') == 'home':
                        home_team = comp.get('team', {}).get('displayName', 'Ev')
                        home_score = comp.get('score', '0')
                    else:
                        away_team = comp.get('team', {}).get('displayName', 'Dep')
                        away_score = comp.get('score', '0')

                full_text += f"• ({time_formatted}) {home_team} {home_score} - {away_score} {away_team}\n"
                league_count += 1
                total_matches += 1

            full_text += "\n"

        if total_matches == 0:
            full_text = "📅 Önümüzdeki 7 gün içinde bültende maç bulunamadı."

        bot.edit_message_text(full_text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ Hata: {e}", chat_id=msg.chat.id, message_id=msg.message_id)

@bot.message_handler(commands=['canli'])
def get_live_matches(message):
    msg = bot.reply_to(message, "🔴 Tüm liglerde ve turnuvalarda canlı maçlar aranıyor...")
    try:
        live_list = []

        for league_name, slug in LEAGUES.items():
            data = fetch_scoreboard(slug)
            if not data or 'events' not in data:
                continue

            for ev in data['events']:
                state = ev.get('status', {}).get('type', {}).get('state', '')
                if state == 'in':  # Maç oynanıyorsa
                    competitions = ev.get('competitions', [{}])[0]
                    competitors = competitions.get('competitors', [])
                    h_name, a_name, h_sc, a_sc = "Ev", "Dep", "0", "0"
                    for comp in competitors:
                        if comp.get('homeAway') == 'home':
                            h_name = comp.get('team', {}).get('displayName')
                            h_sc = comp.get('score', '0')
                        else:
                            a_name = comp.get('team', {}).get('displayName')
                            a_sc = comp.get('score', '0')
                    
                    clock = ev.get('status', {}).get('displayClock', '')
                    live_list.append(f"⚡ *{league_name}* | {h_name} {h_sc} - {a_sc} {a_name} ({clock}')")

        if not live_list:
            bot.edit_message_text("🔴 Şu an canlı oynanan maç bulunmuyor.", chat_id=msg.chat.id, message_id=msg.message_id)
            return

        text = "🔴 *CANLI MAÇLAR*\n\n" + "\n".join(live_list)
        bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ Hata: {e}", chat_id=msg.chat.id, message_id=msg.message_id)

if __name__ == "__main__":
    print("Bot ve Haftalık/Dünya Kupası Servisi Başlatıldı!")
    bot.infinity_polling(none_stop=True, interval=0, timeout=20)
