def fetch_sofascore_data():
    today_str = datetime.now().strftime('%Y-%m-%d')
    # Alternatif Sofascore API endpoint'i
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{today_str}/inverse"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.sofascore.com/',
        'Origin': 'https://www.sofascore.com'
    }
    
    try:
        print("Sofascore alternatif endpoint'ten veriler isteniyor...")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Durum kodu: {response.status_code}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Hata oluştu: {e}")
    return None
