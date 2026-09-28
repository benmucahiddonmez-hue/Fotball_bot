try:bot.set_my_commands([telebot.types.BotCommand('maclar', 'Tüm liglerin maç bülteni'),telebot.types.BotCommand('canli', 'Anlık canlı maçlar'),telebot.types.BotCommand('help', 'Yardım menüsü'),])except Exception:pass
print('Maçkolik Entegreli Bot Başarıyla Başlatıldı!')bot.infinity_polling()
