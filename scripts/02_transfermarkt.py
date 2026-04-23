# Source: https://github.com/dcaribou/transfermarkt-datasets
# Credit: David Cariboo. Data scraped from Transfermarkt and published openly.

# Before running this script:
# Download the data from https://github.com/dcaribou/transfermarkt-datasets and use the following command in the wsl terminal:
# mkdir -p data/raw/transfermarkt_raw && cp /mnt/c/Users/$USER/Downloads/transfermarkt-datasets.zip data/raw/transfermarkt_raw/ && unzip data/raw/transfermarkt_raw/transfermarkt-datasets.zip -d data/raw/transfermarkt_raw/

import pandas as pd

players = pd.read_csv("data/raw/transfermarkt_raw/players.csv.gz")

valuations = pd.read_csv("data/raw/transfermarkt_raw/player_valuations.csv.gz")
valuations["date"] = pd.to_datetime(valuations["date"])
valuations["current_club_id"] = valuations["current_club_id"].fillna(-1).astype(int)

clubs = pd.read_csv("data/raw/transfermarkt_raw/clubs.csv.gz")
games = pd.read_csv("data/raw/transfermarkt_raw/games.csv.gz")

print("Players:", players.shape)
print("Valuations:", valuations.shape)
print("Clubs:", clubs.shape)
print("Games:", games.shape)

# Filter to only include English Premier League clubs

epl_games = games[games["competition_id"] == "GB1"].copy()

# Build Club ID and games table to find market values for players at their respective clubs during the 2022/2023, 2023/2024, and 2024/2025 EPL seasons

club_name_lookup = epl_games.drop_duplicates("home_club_id").set_index("home_club_id")["home_club_name"]

# Filter market values to only include those from the relevant seasons and clubs

seasons = {2022: ("2022-08-01", "2023-06-30"), 2023: ("2023-08-01", "2024-06-30"), 2024: ("2024-08-01", "2025-06-30")}

all_dfs = []

for season, (start, end) in seasons.items():
    season_games = epl_games[epl_games["season"] == int(season)]
    epl_club_ids = season_games["home_club_id"].drop_duplicates().tolist()
    
    mask = ((valuations["date"] >= pd.Timestamp(start)) & (valuations["date"] <= pd.Timestamp(end)) & (valuations["current_club_id"].isin(epl_club_ids)))
    
    df = valuations[mask].copy()
    df["season"] = season

    season_start = pd.to_datetime(start)
    df["days_from_start"] = (df["date"] - season_start).dt.days

    df = (df.sort_values("days_from_start").drop_duplicates(subset=["player_id"], keep="first"))

    df["current_club_name"] = df["current_club_id"].map(club_name_lookup)
          
    all_dfs.append(df)

combined = pd.concat(all_dfs, ignore_index=True)

# Join with player names, market values, and age

player_names = players[["player_id", "name", "date_of_birth", "position"]].copy()

tm_player_merged = pd.merge(combined[["player_id", "season", "market_value_in_eur", "current_club_name", "current_club_id"]], player_names, on="player_id", how="left", indicator=True)

tm_player_values = tm_player_merged[tm_player_merged["_merge"] == "both"].copy()
tm_player_values = tm_player_values.drop(columns=["_merge"])

tm_player_values = tm_player_values.rename(columns={"name" : "player", "current_club_name" : "club", "market_value_in_eur" : "market_value_m"})

# Calculate player age at the start of the season using date of birth and season start date

tm_player_values["date_of_birth"] = pd.to_datetime(tm_player_values["date_of_birth"])

SEASON_START_DATES = {2022: pd.Timestamp("2022-08-01"), 2023: pd.Timestamp("2023-08-01"), 2024: pd.Timestamp("2024-08-01"),}

tm_player_values["season_start"] = tm_player_values["season"].map(SEASON_START_DATES)
tm_player_values["age"] = ((tm_player_values["season_start"] - tm_player_values["date_of_birth"]).dt.days / 365.25).round(1)

tm_player_values = tm_player_values.drop(columns=["season_start", "date_of_birth"])

# Convert market value from euros to millions of euros

tm_player_values["market_value_m"] = tm_player_values["market_value_m"] / 1_000_000

# Drop rows with missing player names or market values

tm_player_values = tm_player_values.dropna(subset=["player", "market_value_m"])
print("tm_player_values shape:", tm_player_values.shape)
print(tm_player_values[["player", "age", "club", "season", "market_value_m"]].head(10).to_string())

# Export player values to csv

tm_player_values.to_csv("data/raw/tm_player_values.csv", index=False)

# Build squad level values by adding all player values per club per season

tm_squad_values = (tm_player_values.groupby(["club", "season"], as_index=False).agg(squad_value_m=("market_value_m", "sum")))

print("tm_squad_values shape:", tm_squad_values.shape)
print(tm_squad_values.head(10).to_string())

# Align season format with Understat

season_format_map = {2022: "2022/2023", 2023: "2023/2024", 2024: "2024/2025"}

tm_player_values["season"] = tm_player_values["season"].map(season_format_map)
tm_squad_values["season"]  = tm_squad_values["season"].map(season_format_map)

print(tm_player_values[["player", "age", "club", "season", "market_value_m"]].head(10).to_string())
print(tm_squad_values.head(10).to_string())

# Export player values to csv

tm_player_values.to_csv("data/raw/tm_player_values.csv", index=False)
tm_squad_values.to_csv("data/raw/tm_squad_values.csv", index=False)
