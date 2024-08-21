import requests


api_key = 'RGAPI-fa1a6451-1a3f-4529-b25b-18139c0e701f'

game_name = 'BlackInter69'
tag_line = 'NA1'

url = f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}'
headers = {'X-Riot-Token': api_key}

response = requests.get(url, headers=headers)

# Print the status code
print(f"Summoner Data Request Status Code: {response.status_code}")

if response.status_code == 200:
    summoner_data = response.json()
    puuid = summoner_data['puuid']
else:
    print("Error fetching summoner data")
    exit()

# Get Match History
match_url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=50&api_key={api_key}'
match_response = requests.get(match_url)

# Print the status code
print(f"Match History Request Status Code: {match_response.status_code}")

if match_response.status_code == 200:
    match_ids = match_response.json()
else:
    print("Error fetching match history")
    exit()

# Fetch Match Details
matches = []
for match_id in match_ids:
    match_detail_url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'
    match_detail_response = requests.get(match_detail_url)

    # Print the status code
    print(f"Match Details Request Status Code for Match ID {match_id}: {match_detail_response.status_code}")

    if match_detail_response.status_code == 200:
        match_details = match_detail_response.json()
        matches.append(match_details)
    else:
        print(f"Error fetching match details for match ID: {match_id}")

print(f"Retrieved {len(matches)} matches.")
