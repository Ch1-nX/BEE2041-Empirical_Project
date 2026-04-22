# Before running this script, create the output folder by running the following in wsl terminal: mkdir -p data/raw

import soccerdata as sd
import pandas as pd

# Begin using soccerdata to get data from understat.com

from soccerdata import Understat

# Looking for data from 2022/2023, 2023/2024, and 2024/2025 seasons of the English Premier League

seasons = [2022, 2023, 2024]

all_dfs = []  # To store dataframes for later combination

# Loop through seasons and save data to csv files

for season in seasons:
    u = sd.Understat(leagues="ENG-Premier League", seasons=season) # "u" for "understat"
    df = u.read_player_season_stats()
    df = df.reset_index()
    df["season"] = f"{season}/{season+1}"
    all_dfs.append(df)

combined = pd.concat(all_dfs, ignore_index=True)

combined.to_csv("data/raw/understat_player_stats.csv", index=False)

print(combined.head())
print(combined.shape)
print(combined.columns)
print(combined["season"].value_counts())