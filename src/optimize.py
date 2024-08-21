import requests
import pandas as pd
import matplotlib.pyplot as plt
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

        # Extracting participant information
        participant_data = None
        for participant in match_details['info']['participants']:
            if participant['puuid'] == puuid:
                participant_data = participant
                break

        # Extracting win/loss and game datetime
        win_status = participant_data['win']
        game_datetime = match_details['info']['gameStartTimestamp']

        # Convert timestamp to readable format
        from datetime import datetime
        game_datetime = datetime.utcfromtimestamp(game_datetime / 1000).strftime('%Y-%m-%d %H:%M:%S')

        # Append match details including win/loss and datetime
        matches.append({
            'match_id': match_id,
            'win': win_status,
            'datetime': game_datetime,
            'match_details': match_details
        })
    else:
        print(f"Error fetching match details for match ID: {match_id}")

# Example: Print the first match's win/loss and datetime
for match in matches:
    print(f"Match ID: {match['match_id']}, Win: {match['win']}, DateTime: {match['datetime']}")

print(f"Retrieved {len(matches)} matches.")


#Create Df
matches2 = pd.DataFrame(matches)
matches2.to_csv('matches.csv')

# Convert to DataFrame
df = pd.DataFrame(matches)

# Convert the datetime to a pandas datetime object and extract the date
df['datetime'] = pd.to_datetime(df['datetime'])
df['date'] = df['datetime'].dt.date

# Initialize a plot
plt.figure(figsize=(12, 8))

# Group the data by date
for date, group in df.groupby('date'):
    # Sort by datetime within each group
    group = group.sort_values('datetime')
    
    # Calculate cumulative wins and total games played for the day
    group['cumulative_wins'] = group['win'].cumsum()
    group['total_games'] = range(1, len(group) + 1)
    
    # Calculate cumulative win rate
    group['cumulative_win_rate'] = group['cumulative_wins'] / group['total_games'] * 100
    
    # Plot the cumulative win rate for this day
    plt.plot(group['total_games'], group['cumulative_win_rate'], marker='o', linestyle='-', label=f'{date}')
    
# Adding title and labels
plt.title('Cumulative Win Rate Over Games (Separated by Day)')
plt.xlabel('Game Number (Per Day)')
plt.ylabel('Cumulative Win Rate (%)')
plt.ylim(0, 100)  # Set y-axis limits to 0-100%
plt.grid(True)
plt.legend(title='Date')

# Show the plot
plt.tight_layout()
plt.show()
