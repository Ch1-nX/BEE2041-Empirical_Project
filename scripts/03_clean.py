# Before running this script, create the output folder by running the following in wsl terminal: mkdir -p data/clean

import numpy as np
import pandas as pd

# Load initial datasets from raw folder

understat  = pd.read_csv("data/raw/understat_player_stats.csv")
tm_players = pd.read_csv("data/raw/tm_player_values.csv")
tm_squads  = pd.read_csv("data/raw/tm_squad_values.csv")

print("\nRaw Dataset Shapes:")
print("Understat rows: " + str(understat.shape[0]))
print("Understat players: ", len(understat))
print("TM players rows: " + str(tm_players.shape[0]))
print("TM squads rows: " + str(tm_squads.shape[0]))

# Filter to remove players with less than 270 minutes

understat = understat.loc[understat["minutes"] >= 270]
understat.reset_index(drop=True, inplace=True)
print("\nUnderstat players after filtering (<270 min): ", len(understat))

# Inspect datasets to understand structure, check for missing values and identify any cleaning steps needed before merging

print("\nUnderstat info:")
understat.info()

print("\nUnderstat describe: " + str(understat.describe()))

print("\nTM Players - first 5 rows: " + str(tm_players.head()))

print("\nTM Squads - first 5 rows:" + str(tm_squads.head()))

# Check for missing values in TM datasets and drop rows with missing values in key columns

print("\nMissing Values in TM Data:")
print("tm_players missing market_value_m: " + str(tm_players["market_value_m"].isna().sum()))
print("tm_squads missing squad_value_m : " + str(tm_squads["squad_value_m"].isna().sum()))

tm_players = tm_players.dropna(subset=["market_value_m"])
tm_squads  = tm_squads.dropna(subset=["squad_value_m"])

# Standardise club names
# TM dataset uses long names whilst Understat (soccerdata) uses short names
# Map TM long names to Understat short names for merging

CLUB_NAME_MAP = {
    "Arsenal Football Club": "Arsenal",
    "Association Football Club Bournemouth": "Bournemouth",
    "Aston Villa Football Club": "Aston Villa",
    "Brentford Football Club": "Brentford",
    "Brighton and Hove Albion Football Club": "Brighton",
    "Burnley Football Club": "Burnley",
    "Chelsea Football Club": "Chelsea",
    "Crystal Palace Football Club": "Crystal Palace",
    "Everton Football Club": "Everton",
    "Fulham Football Club": "Fulham",
    "Ipswich Town": "Ipswich",
    "Leeds United Association Football Club": "Leeds",
    "Leicester City": "Leicester",
    "Liverpool Football Club": "Liverpool",
    "Luton Town": "Luton",
    "Manchester City Football Club": "Manchester City",
    "Manchester United Football Club": "Manchester United",
    "Newcastle United Football Club": "Newcastle United",
    "Nottingham Forest Football Club": "Nottingham Forest",
    "Sheffield United": "Sheffield United",
    "Southampton FC": "Southampton",
    "Tottenham Hotspur Football Club": "Tottenham",
    "West Ham United Football Club": "West Ham",
    "Wolverhampton Wanderers Football Club": "Wolverhampton Wanderers",
}

# Apply mapping to create standardised club column for merging
tm_players["club_std"] = tm_players["club"].map(CLUB_NAME_MAP)
tm_squads["club_std"]  = tm_squads["club"].map(CLUB_NAME_MAP)

# Understat uses team column for club name so create a "club_std" column in Understat by copying "team" for consistency with TM datasets
understat["club_std"]  = understat["team"]

print("\nUnmapped Clubs:")
print("tm_players unmapped: " + str(tm_players["club_std"].isna().sum()))
print("tm_squads unmapped: " + str(tm_squads["club_std"].isna().sum()))

# Standardise player names for merging
# Replace accented characters with normal equivalent

def normalise_name(name):
    
    if not isinstance(name, str):
        return ""

    name = name.strip().lower()

    # Remove HTML entities
    name = name.replace("&#039;", "").replace("&amp;", "")

    # Replace accented characters
    name = name.replace("á", "a").replace("é", "e").replace("í", "i")
    name = name.replace("ó", "o").replace("ú", "u")
    name = name.replace("à", "a").replace("è", "e").replace("ì", "i")
    name = name.replace("ò", "o").replace("ù", "u")
    name = name.replace("â", "a").replace("ê", "e").replace("î", "i")
    name = name.replace("ô", "o").replace("û", "u")
    name = name.replace("ä", "a").replace("ë", "e").replace("ï", "i")
    name = name.replace("ö", "o").replace("ü", "u")
    name = name.replace("ã", "a").replace("õ", "o").replace("ñ", "n")
    name = name.replace("ø", "o").replace("å", "a").replace("æ", "ae")
    name = name.replace("č", "c").replace("ć", "c").replace("š", "s")
    name = name.replace("ś", "s").replace("ž", "z").replace("ź", "z")
    name = name.replace("ř", "r").replace("ě", "e").replace("ý", "y")
    name = name.replace("ť", "t").replace("ď", "d").replace("ň", "n")
    name = name.replace("ł", "l").replace("ń", "n")
    name = name.replace("ğ", "g").replace("ş", "s").replace("ı", "i")
    name = name.replace("i\u0307", "i").replace("j\u0307", "j")
    name = name.replace("ă", "a").replace("ș", "s").replace("ț", "t")

    # Remove punctuation
    name = name.replace(".", "").replace("-", " ").replace("'", "")

    # Turn multiple spaces into one
    name = " ".join(name.split())
    return name

tm_players["player_key"] = tm_players["player"].apply(normalise_name)
understat["player_key"]  = understat["player"].apply(normalise_name)

# Manual name correction for odd cases

NAME_CORRECTIONS = {
    # TM uses full name whilst Understat only uses first name
    "kepa arrizabalaga": "kepa",

    # TM uses full names whilst Understat uses short names
    "maximilian kilman": "max kilman",
    "stefan ortega moreno": "stefan ortega",
    "destiny udogie": "iyenoma destiny udogie",
    "amad diallo": "amad diallo traore",
    "vinicius tobias de paiva souza": "vinicius souza",
    "vinicius tobias souza": "vinicius souza",

    # TM uses nicknames whilst Understat uses full names
    "tino livramento": "valentino livramento",
    "matty cash": "matthew cash",
    "ansu fati": "anssumane fati",
    "heung min son": "son heung min",

    # TM leaves out parts of names whilst Understat uses full names
    "cheick doucoure": "cheick oumar doucoure",
    "pape matar sarr": "pape sarr",
    "benoit badiashile": "benoit badiashile mukinayi",
    "joe aribo": "joe ayodele aribo",
    "lesley ugochukwu": "chimuanya ugochukwu",
    "savio moreira de oliveira": "savio",
    "savio moreira": "savio",
    "jaden philogene": "jaden philogene bidace",
    "joe gomez": "joseph gomez",
    "ezri konsa": "ezri konsa ngoyo",

    # TM uses full names whilst Understat onlyuses surnames
    "pervis estupinan": "estupinan",
    "emerson royal": "emerson",

    # TM uses full surnames whilst Understat uses shortened surnames
    "bobby decordova reid": "bobby reid",
    "bobby de cordova reid": "bobby reid",

    # Alternate translations
    "illya zabarnyi": "illia zabarnyi",
    "ilya zabarnyi": "illia zabarnyi",
    "vitaliy mykolenko": "vitalii mykolenko",
    "mykhaylo mudryk": "mykhailo mudryk",
    "nayef aguerd": "naif aguerd",
    "jonny otto": "jonny",
    "hamed traore": "hamed junior traore",
    "arnaut danjuma": "arnaut danjuma groeneveld",
    "ryan giles": "ryan john giles",
    "stefan ortega": "stefan ortega moreno",
    "benoit badiashile": "benoit badiashile mukinayi",
}

# Apply corrections for merging
tm_players["player_key"] = tm_players["player_key"].replace(NAME_CORRECTIONS)

print("\nSample Normalised Names - Transfermarkt:")
print(tm_players[["player", "player_key"]].head(15).to_string())

print("\nSample Normalised Names - Understat:")
print(understat[["player", "player_key"]].head(15).to_string())

# Convert columns in Understat from string to numeric

numeric_cols = ["matches", "minutes", "goals", "assists", "xg", "xa", "np_xg", "np_goals", "key_passes", "yellow_cards", "red_cards",]

for col in numeric_cols:
    if col in understat.columns:
        understat[col] = pd.to_numeric(understat[col], errors="coerce")

# Merge player datasets from Understat and Transfermarkt on player_key + club + season, only keeping matched rows

players_merged = pd.merge(understat, tm_players[["player_key", "club_std", "season", "market_value_m", "age"]], on=["player_key", "club_std", "season"], how="left", indicator=True,)

print("\nMerge result:")
print(players_merged["_merge"].value_counts())

unmatched = players_merged[players_merged["_merge"] == "left_only"].copy()
print("\nUnmatched players by minutes:")
print(unmatched[["player", "club_std", "season", "minutes"]].sort_values("minutes", ascending=False).head(20).to_string())

players = players_merged[players_merged["_merge"] == "both"].copy()
players = players.drop(columns=["_merge"])

print("\nRows after keeping matched only: " + str(len(players)))

# Secondary merge for loan players
# Some players appear in Understat at their loan club but in TM they appearat their parent club. 

unmatched_rows = players_merged[players_merged["_merge"] == "left_only"].copy()
unmatched_rows = unmatched_rows.drop(columns=["_merge", "market_value_m", "age"])

# Merge on player_key and season only, ignoring club to find TM value for unmatched players,
tm_no_club = tm_players[["player_key", "season", "market_value_m", "age"]].copy()

# Drop duplicates keeping the first TM value found.
tm_no_club = (tm_no_club.sort_values("market_value_m", ascending=False).drop_duplicates(subset=["player_key", "season"], keep="first"))

secondary_merged = pd.merge(unmatched_rows, tm_no_club, on=["player_key", "season"], how="left",)
secondary_matched = secondary_merged[secondary_merged["market_value_m"].notna()].copy()

print("\nSecondary Merge:")
print("Unmatched from initial merge: " + str(len(unmatched_rows)))
print("Recovered from secondary merge: " + str(len(secondary_matched)))
print(secondary_matched[["player", "club_std", "season", "market_value_m"]].to_string())

# Combine primary and secondary matched rows
players = pd.concat([players, secondary_matched],ignore_index=True)
print("\nTotal rows after secondary merge: " + str(len(players)))

# Create analytical variables

# Calculate average squad age per club per season
squad_age = (players[players["age"].notna()].groupby(["club_std", "season"], as_index=False).agg(avg_age=("age", "mean")))
squad_age["avg_age"] = squad_age["avg_age"].round(1)

# Calculate nineties for per90 stats
players["nineties"] = players["minutes"] / 90

# per90 stats
players["goals_p90"] = players["goals"] / players["nineties"]
players["assists_p90"] = players["assists"] / players["nineties"]
players["xg_p90"] = players["xg"] / players["nineties"]
players["xa_p90"] = players["xa"] / players["nineties"]
players["npxg_p90"] = players["np_xg"] / players["nineties"]
players["kp_p90"] = players["key_passes"] / players["nineties"]

# Calculate Log market value to account for skewed distribution of player values
players["log_market_value"] = np.log(players["market_value_m"])

# Simplify positions into 4 categories
pos_map = {
    "F S": "Forward",
    "F": "Forward",
    "S": "Forward",
    "AM S": "Midfielder",
    "M S": "Midfielder",
    "M": "Midfielder",
    "D S": "Defender",
    "D": "Defender",
    "GK": "Goalkeeper",
}

players["position_clean"] = players["position"].map(pos_map).fillna("Midfielder")

print("\nPosition value counts after cleaning:")
print(players["position_clean"].value_counts())

# Build squad dataset using the TM squad values dataset and merging with standings and points data from online to get points per season for each club

STANDINGS = {
    "2022/2023": {
        "Manchester City": 89, "Arsenal": 84, "Manchester United": 75,
        "Newcastle United": 71, "Liverpool": 67, "Brighton": 62,
        "Aston Villa": 61, "Tottenham": 60, "Brentford": 59,
        "Fulham": 52, "Crystal Palace": 45, "Chelsea": 44,
        "Wolverhampton Wanderers": 41, "West Ham": 40,
        "Bournemouth": 39, "Nottingham Forest": 38,
        "Everton": 36, "Leicester": 34, "Leeds": 31, "Southampton": 25,
    },
    "2023/2024": {
        "Manchester City": 91, "Arsenal": 89, "Liverpool": 82,
        "Aston Villa": 68, "Tottenham": 66, "Chelsea": 63,
        "Newcastle United": 60, "Manchester United": 60,
        "West Ham": 52, "Crystal Palace": 49, "Brighton": 48,
        "Bournemouth": 48, "Fulham": 47, "Wolverhampton Wanderers": 46,
        "Everton": 40, "Brentford": 39, "Nottingham Forest": 32,
        "Luton": 26, "Burnley": 24, "Sheffield United": 16,
    },
    "2024/2025": {
    "Liverpool": 84, "Arsenal": 74, "Manchester City": 71,
    "Chelsea": 69, "Newcastle United": 66, "Aston Villa": 66,
    "Nottingham Forest": 65, "Brighton": 61, "Bournemouth": 56,
    "Brentford": 56, "Fulham": 54, "Crystal Palace": 53,
    "Everton": 48, "West Ham": 43, "Manchester United": 42,
    "Wolverhampton Wanderers": 42, "Tottenham": 38, "Leicester": 25,
    "Ipswich": 22, "Southampton": 12,
},
}

# Build standings as a DataFrame for merging with squad values
standings_rows = []
for season, clubs in STANDINGS.items():
    for club, points in clubs.items():
        standings_rows.append({"club_std": club, "season":   season, "points":   points,})
standings_df = pd.DataFrame(standings_rows)

# Merge squad values with standings
squads_merged = pd.merge(tm_squads[["club_std", "season", "squad_value_m"]].dropna(), standings_df, on=["club_std", "season"], how="left", indicator=True,)

print("\nSquad Merge result:")
print(squads_merged["_merge"].value_counts())

squads = squads_merged[squads_merged["_merge"] == "both"].copy()
squads = squads.drop(columns=["_merge"])

# Merge average squad age onto squad dataset
squads = pd.merge(squads, squad_age, on=["club_std", "season"], how="left")

# Calculate Log squad value
squads["log_squad_value"] = np.log(squads["squad_value_m"])

print("\nSquad rows: " + str(len(squads)))
print(squads[["club_std", "season", "squad_value_m", "points"]].head(8).to_string())

# Final inspection of cleaned datasets before exporting

print("\nFinal players dataset:")
print(players[["market_value_m", "log_market_value", "goals_p90", "xg_p90", "npxg_p90", "minutes",]].describe())

print("\nMissing values in final players dataset:")
print(players.isna().sum())

print("\nFinal player columns:")
print(list(players.columns))

# Export cleaned datasets to clean folder

players.to_csv("data/clean/players.csv", index=False)
squads.to_csv("data/clean/squads.csv",   index=False)

print("\nSaved " + str(len(players)) + " player rows -> data/clean/players.csv")
print("Saved " + str(len(squads)) + " squad rows  -> data/clean/squads.csv")