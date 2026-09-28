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
