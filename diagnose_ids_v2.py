
import utils
import requests
import json

def fetch_market():
    url = "https://api.cartola.globo.com/atletas/mercado"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json().get('atletas', [])
    except:
        pass
    return []

def main():
    players = fetch_market()
    print(f"Total players in market: {len(players)}")
    
    targets = [
        "Rincón", "Neymar", "Barreal", "Thaciano", "Miguelito", "Rollheiser", 
        "Zé Rafael", "João Schmidt", "Diógenes", "Gabriel Brazão", "Maik", 
        "Mayke", "Souza", "Fagner", "Marlon", "Aguirre", "Alisson", "Escobar"
    ]
    
    norm_targets = {utils.normalize_name(t): t for t in targets}
    
    missing_ids = {}
    
    for p in players:
        nick = p.get('apelido', '')
        name = p.get('nome', '')
        cid = str(p.get('clube_id'))
        
        # Check against mapped clubs
        mapped_name = utils.CLUB_MAP.get(cid, "Outros")
        
        # Check if target
        p_norm = utils.normalize_name(nick)
        
        # Exact or partial match for targets
        is_target = False
        for vt in norm_targets:
            if vt in p_norm:
                is_target = True
                break
                
        if is_target:
            print(f"TARGET FOUND: {nick} | ID: {cid} | Mapped: {mapped_name}")
            
        if mapped_name == "Outros":
            if cid not in missing_ids:
                missing_ids[cid] = []
            if len(missing_ids[cid]) < 3:
                missing_ids[cid].append(nick)

    print("\n--- UNMAPPED CLUBS (Outros) ---")
    for cid, examples in missing_ids.items():
        print(f"Club ID {cid}: {examples}")

if __name__ == "__main__":
    main()
