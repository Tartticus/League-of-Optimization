import requests
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # Make sure Pillow is installed
from io import BytesIO  # To handle image data from requests
import requests

api_key = 'RGAPI-a6746745-332a-4aac-9c99-6166b0494f0c'
con = duckdb.connect('builds.db')
game_name = 'MenstrationFan69'
tag_line = '9616'

# Download the item JSON to map item IDs to names
item_url = "http://ddragon.leagueoflegends.com/cdn/13.19.1/data/en_US/item.json"
item_response = requests.get(item_url)
item_data = item_response.json()['data']

# Function to get champion image URL
def get_champion_image_url(champion_name):
    return f"http://ddragon.leagueoflegends.com/cdn/13.19.1/img/champion/{champion_name}.png"

# Function to get item image URL
def get_item_image_url(item_id):
    return f"http://ddragon.leagueoflegends.com/cdn/13.19.1/img/item/{item_id}.png"


def download_image(url, size=(64, 64)):
    response = requests.get(url, stream=True)
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    img = img.resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)

# Function to display items
def display_items(best_build):
    for widget in item_frame.winfo_children():
        widget.destroy()
    if best_build:
        for i, item_id in enumerate(best_build[:6]):
            if item_id != 0:
                item_url = get_item_image_url(item_id)
                item_image = download_image(item_url)
                item_label = tk.Label(item_frame, image=item_image)
                item_label.image = item_image
                item_label.grid(row=0, column=i)

# Function to update the champion image
def update_champion_image(champion_name):
    image_url = get_champion_image_url(champion_name)
    champion_image = download_image(image_url, size=(128, 128))
    champion_image_label.config(image=champion_image)
    champion_image_label.image = champion_image

# Function to get item name from item id
def get_item_name(item_id):
    return item_data[str(item_id)]['name'] if str(item_id) in item_data else "Unknown Item"

# Create the table to store build data if it doesn't exist
con.execute('''
CREATE TABLE IF NOT EXISTS ChampionBuilds (
    match_id VARCHAR PRIMARY KEY,
    champion_name VARCHAR,
    opponent_champion VARCHAR,
    item0 INT,
    item1 INT,
    item2 INT,
    item3 INT,
    item4 INT,
    item5 INT,
    win BOOLEAN,
    match_datetime TIMESTAMP
);
''')

# Fetch summoner PUUID
url = f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={api_key}'
headers = {'X-Riot-Token': api_key}
response = requests.get(url)

if response.status_code == 200:
    summoner_data = response.json()
    puuid = summoner_data['puuid']
else:
    print("Error fetching summoner data")
    exit()

# Get match history
match_url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=50&api_key={api_key}'
match_response = requests.get(match_url)

if match_response.status_code == 200:
    match_ids = match_response.json()
else:
    print("Error fetching match history")
    exit()

# Fetch match details and save builds to DuckDB
for match_id in match_ids:
    # Check if match_id already exists in the database
    result = con.execute('SELECT COUNT(*) FROM ChampionBuilds WHERE match_id = ?', (match_id,)).fetchone()

    if result[0] == 0:  # If match_id doesn't exist, insert the data
        match_detail_url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'
        match_detail_response = requests.get(match_detail_url)

        if match_detail_response.status_code == 200:
            match_details = match_detail_response.json()
            participant_data = None
            opponent_champion = None

            # Find your team ID
            my_team_id = None
            for participant in match_details['info']['participants']:
                if participant['puuid'] == puuid:
                    participant_data = participant
                    my_team_id = participant['teamId']
                    break

            # Get the opponent champion (same lane, opposite team)
            for participant in match_details['info']['participants']:
                if participant['teamId'] != my_team_id and participant['lane'] == participant_data['lane']:
                    opponent_champion = participant['championName']
                    break

            if participant_data:
                game_timestamp = match_details['info']['gameCreation'] // 1000
                match_datetime = datetime.fromtimestamp(game_timestamp)
                champion_name = participant_data['championName']
                build = [
                    participant_data['item0'],
                    participant_data['item1'],
                    participant_data['item2'],
                    participant_data['item3'],
                    participant_data['item4'],
                    participant_data['item5']
                ]
                win = participant_data['win']

                # Insert the match data into the database
                con.execute('''
                INSERT INTO ChampionBuilds 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', [match_id, champion_name, opponent_champion, *build, win, match_datetime])

# Function to get the best items used by you based on win rate against an opponent champion
def get_best_items_against(opponent_champion):
    query = '''
    SELECT item0, item1, item2, item3, item4, item5, COUNT(*) as matches, 
           SUM(CASE WHEN win THEN 1 ELSE 0 END) as wins
    FROM ChampionBuilds
    WHERE opponent_champion = ?
    GROUP BY item0, item1, item2, item3, item4, item5
    ORDER BY wins DESC, matches DESC
    LIMIT 1
    '''
    result = con.execute(query, (opponent_champion,)).fetchall()
    return result[0] if result else []

# Function to update the suggested items when an opponent champion is selected
def update_items(*args):
    opponent_champion = champion_var.get()
    if opponent_champion != "Select a Champion":
        best_build = get_best_items_against(opponent_champion)
        if best_build:
            print(f"Displaying build for {opponent_champion}")
            display_items(best_build)
            update_champion_image(opponent_champion)
            win_rate = best_build[7] / best_build[6] * 100 if best_build[6] > 0 else 0
            result_text.set(f"Best Build Against {opponent_champion}:\nWin Rate: {win_rate:.2f}%")
        else:
            result_text.set("No match data for this opponent champion.")
    else:
        result_text.set("")



# Set up the Tkinter window
root = tk.Tk()
root.title("Vlad Build Optimizer")

champion_image_label = tk.Label(root)
champion_image_label.pack(pady=10)

item_frame = tk.Frame(root)
item_frame.pack(pady=10)

result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify="left")
result_label.pack(pady=10)

# Label for dropdown
label = tk.Label(root, text="Select an Opponent Champion:")
label.pack(pady=10)
champion_var = tk.StringVar()
champion_dropdown = ttk.Combobox(root, textvariable=champion_var)
# Full list of champions
champions = [
    "Aatrox", "Ahri", "Akali", "Akshan", "Alistar", "Amumu", "Anivia", "Annie",
    "Aphelios", "Ashe", "Aurelion Sol", "Azir", "Bard", "Bel'Veth", "Blitzcrank", "Brand",
    "Braum", "Briar", "Caitlyn", "Camille", "Cassiopeia", "Cho'Gath", "Corki", "Darius",
    "Diana", "Dr. Mundo", "Draven", "Ekko", "Elise", "Evelynn", "Ezreal", "Fiddlesticks",
    "Fiora", "Fizz", "Galio", "Gangplank", "Garen", "Gnar", "Gragas", "Graves", "Gwen",
    "Hecarim", "Heimerdinger", "Illaoi", "Irelia", "Ivern", "Janna", "Jarvan IV", "Jax", 
    "Jayce", "Jhin", "Jinx", "Kai'Sa", "Kalista", "Karma", "Karthus", "Kassadin", "Katarina", 
    "Kayle", "Kayn", "Kennen", "Kha'Zix", "Kindred", "Kled", "Kog'Maw", "LeBlanc", "Lee Sin", 
    "Leona", "Lillia", "Lissandra", "Lucian", "Lulu", "Lux", "Malphite", "Malzahar", "Maokai", 
    "Master Yi", "Miss Fortune", "Mordekaiser", "Morgana", "Nami", "Nasus", "Nautilus", "Neeko",
    "Nocturne", "Nunu & Willump", "Olaf", "Orianna", "Ornn", "Pantheon", "Poppy", "Pyke",
    "Rakan", "Rammus", "Renekton", "Rengar", "Riven", "Ryze", "Samira", "Sejuani", "Senna", 
    "Seraphine", "Sett", "Shaco", "Shen", "Shyvana", "Singed", "Sion", "Sivir", "Skarner", 
    "Sona", "Soraka", "Swain", "Sylas", "Syndra", "Tahm Kench", "Taliyah", "Talon", "Taric", 
    "Teemo", "Thresh", "Tristana", "Tryndamere", "Twisted Fate", "Twitch", "Udyr", "Urgot", 
    "Varus", "Vayne", "Veigar", "Vel'Koz", "Vi", "Viego", "Viktor", "Vladimir", "Volibear", 
    "Warwick", "Wukong", "Xayah", "Xerath", "Xin Zhao", "Yasuo", "Yone", "Yorick", "Zac", 
    "Zed", "Zeri", "Ziggs", "Zilean", "Zoe", "Zyra", "Aurora"
]

champion_dropdown['values'] = ["Select a Champion"] + champions
champion_dropdown.current(0)
champion_dropdown.pack(pady=10)

# Bind the function to update items when a champion is selected
champion_var.trace('w', update_items)


# Label to display suggested items
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify="left")
result_label.pack(pady=10)

# Run the Tkinter loop
root.mainloop()
