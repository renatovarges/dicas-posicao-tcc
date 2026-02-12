
import requests
import json
import collections

def main():
    url = "https://api.cartola.globo.com/atletas/mercado"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        data = resp.json().get('atletas', [])
    except Exception as e:
        print(f"Error: {e}")
        return

    clubs = collections.defaultdict(list)
    for p in data:
        cid = str(p.get('clube_id'))
        nick = p.get('apelido', 'Unknown')
        clubs[cid].append(nick)
        
    with open("club_dump.txt", "w", encoding="utf-8") as f:
        f.write(f"Found {len(clubs)} unique Club IDs.\n\n")
        # Sort by ID
        for cid in sorted(clubs.keys(), key=lambda x: int(x) if x.isdigit() else 9999):
            players = clubs[cid]
            # List up to 10 players
            players_str = ', '.join(players[:10])
            line = f"ID {cid.ljust(5)} ({len(players)} players): {players_str}\n"
            print(line.strip())
            f.write(line)

if __name__ == "__main__":
    main()
