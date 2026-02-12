
import utils
import pandas as pd
import requests

# Fetch market data
print("Fetching market data to identify missing teams...")
try:
    data = utils.fetch_mercado_data()
    
    missing_teams = {}
    
    for atleta in data:
        club_id = str(atleta.get('clube_id'))
        team_name = utils.CLUB_MAP.get(club_id, 'Outros')
        
        if team_name == 'Outros':
            # Store the ID and a sample player to help identify the team
            if club_id not in missing_teams:
                missing_teams[club_id] = []
            if len(missing_teams[club_id]) < 5: # Keep first 5 players
                missing_teams[club_id].append(atleta.get('apelido', 'Unknown'))
                
    with open("missing_teams.txt", "w", encoding="utf-8") as f:
        f.write("--- Missing IDs found ---\n")
        for cid, players in missing_teams.items():
            line = f"ID {cid}: Players {players}\n"
            print(line)
            f.write(line)

except Exception as e:
    print(f"Error: {e}")
