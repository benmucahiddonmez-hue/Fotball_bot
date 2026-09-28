import requests
import telebot

# Telegram Bot Token'ını buraya yaz
TELEGRAM_TOKEN = '8575255003:AAGp9pQqRcOnJNnS4BJ6TiB536-idtXw7JI'

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def fetch_mackolik_data():
  url = 'https://widget.shamsports.com/livedata'
  headers = {
      'User-Agent': (
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
          ' (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      ),
      'Referer': 'https://www.mackolik.com/',
  }
  try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
      return response.json()
  except Exception:
    pass
  return None


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  text = (
      '⚽ *Futbol Botuna Hoş Geldiniz!*\n\n'
      '📌 *Komutlar:*\n'
      '• `/maclar` — Günün maç bülteni\n'
      '• `/canli` — Anlık canlı maçlar\n'
  )
  bot.reply_to(message, text, parse_mode='Markdown')


@bot.message_handler(commands=['maclar'])
def get_all_matches(message):
  msg = bot.reply_to(message, '⏳ Bülten çekiliyor...')
  try:
    data = fetch_mackolik_data()
    if not data or 'm' not in data:
      bot.edit_message_text(
          '❌ Bülten alınamadı.',
          chat_id=msg.chat.id,
          message_id=msg.message_id,
      )
      return

    matches = data['m']
    text = '⚽ *MAÇ BÜLTENİ*\n\n'
    count = 0
    for m in matches[:10]:
      home = m[1] if len(m) > 1 else 'Ev'
      away = m[2] if len(m) > 2 else 'Dep'
      time_str = m[6] if len(m) > 6 else ''
      text += f'• {home} vs {away} (⏰ {time_str})\n'
      count += 1

    if count == 0:
      text = '📅 Bugün maç bulunamadı.'

    bot.edit_message_text(
        text,
        chat_id=msg.chat.id,
        message_id=msg.message_id,
        parse_mode='Markdown',
    )
  except Exception as e:
    bot.edit_message_text(
        f'❌ Hata: {e}', chat_id=msg.chat.id, message_id=msg.message_id
    )


@bot.message_handler(commands=['canli'])
def get_live_matches(message):
  msg = bot.reply_to(message, '⏳ Canlı maçlar kontrol ediliyor...')
  try:
    data = fetch_mackolik_data()
    if not data or 'm' not in data:
      bot.edit_message_text(
          '❌ Canlı skor alınamadı.',
          chat_id=msg.chat.id,
          message_id=msg.message_id,
      )
      return

    live_matches = []
    for m in data['m']:
      status = str(m[3]) if len(m) > 3 else ''
      if (
          'MS' not in status
          and 'Ert' not in status
          and status != ''
          and status != '0'
      ):
        home = m[1] if len(m) > 1 else ''
        away = m[2] if len(m) > 2 else ''
        sh = m[4] if len(m) > 4 else '0'
        sa = m[5] if len(m) > 5 else '0'
        live_matches.append(f'⚡ *{home}* {sh} - {sa} *{away}* ({status})')

    if not live_matches:
      bot.edit_message_text(
          '🔴 Şu anda canlı maç yok.',
          chat_id=msg.chat.id,
          message_id=msg.message_id,
      )
      return

    text = '🔴 *CANLI MAÇLAR*\n\n' + '\n'.join(live_matches[:10])
    bot.edit_message_text(
        text,
        chat_id=msg.chat.id,
        message_id=msg.message_id,
        parse_mode='Markdown',
    )
  except Exception as e:
    bot.edit_message_text(
        f'❌ Hata: {e}', chat_id=msg.chat.id, message_id=msg.message_id
    )


print('Bot Başarıyla Başlatıldı!')
bot.infinity_polling()
