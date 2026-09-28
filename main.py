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
    print("İstek atılıyor...")  # Loglarda görebilmek için
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Durum kodu: {response.status_code}")  # Gelen HTTP kodunu yazdır
    if response.status_code == 200:
      return response.json()
  except Exception as e:
    print(f"Hata oluştu: {e}")  # Hatayı loglara bas
  return None
