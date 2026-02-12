
import requests
import json

url = "https://api.cartola.globo.com/clubes"
try:
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        data = response.json()
        print("--- Clubes Found ---")
        
        # Structure is Dict[ID, Data]
        # Data has 'nome', 'abreviacao', etc.
        
        found_map = {}
        for cid, info in data.items():
            name = info.get('nome', 'Unknown')
            found_map[cid] = name
            
        # Print relevant clubs (Serie A/B/C)
        # Just print all to be safe
        for cid, name in found_map.items():
            print(f"'{cid}': '{name}',")
            
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
