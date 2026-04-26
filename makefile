# Makefile for BEE2041 Empirical Project

# On Windows with WSL and Anaconda, run:
# PYTHON=/mnt/c/Users/$USER/anaconda3/python.exe make

PYTHON ?= python

all: docs/index.html

data/raw/understat_player_stats.csv: scripts/01_soccerdata.py
	$(PYTHON) scripts/01_soccerdata.py

data/raw/tm_player_values.csv: scripts/02_transfermarkt.py \
	data/raw/transfermarkt_raw/players.csv.gz \
	data/raw/transfermarkt_raw/player_valuations.csv.gz \
	data/raw/transfermarkt_raw/clubs.csv.gz \
	data/raw/transfermarkt_raw/games.csv.gz
	$(PYTHON) scripts/02_transfermarkt.py

data/clean/players.csv: scripts/03_clean.py \
	data/raw/understat_player_stats.csv \
	data/raw/tm_player_values.csv
	$(PYTHON) scripts/03_clean.py

figures/fig1_summary_statistics.png: scripts/04_analyse.py \
	data/clean/players.csv \
	data/clean/squads.csv
	$(PYTHON) scripts/04_analyse.py

docs/index.html: blog.ipynb \
	figures/fig1_summary_statistics.png
	$(PYTHON) -m jupyter nbconvert --to html blog.ipynb --output docs/index.html