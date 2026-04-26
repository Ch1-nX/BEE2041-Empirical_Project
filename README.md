# Player Valuation and Squad Spending: What Really Predicts Success in the Premier League?
 
A data driven analysis of the Premier League across the 2022/23, 2023/24, and 2024/25 seasons, exploring what performance metrics actually drive player market values, and whether squad value directly leads to success in the league.
 
Blog post: https://Ch1-nX.github.io/BEE2041-Empirical_Project
 
## Installation
 
```bash
git clone https://github.com/Ch1-nX/BEE2041-Empirical_Project.git
cd BEE2041-Empirical_Project
pip install pandas numpy matplotlib statsmodels soccerdata jupyter
```
 
## Usage
 
Before running any scripts, create the required folders:
 
```bash
mkdir -p data/raw data/clean figures docs
```

Download "transfermarkt-datasets.zip" from https://github.com/dcaribou/transfermarkt-datasets into your "Downloads" folder and unzip into "data/raw/transfermarkt_raw/":

```bash
mkdir -p data/raw/transfermarkt_raw && cp /mnt/c/Users/$USER/Downloads/transfermarkt-datasets.zip data/raw/transfermarkt_raw/ && unzip data/raw/transfermarkt_raw/transfermarkt-datasets.zip -d data/raw/transfermarkt_raw/
```

Run the scripts in order:
 
```bash
python scripts/01_soccerdata.py
python scripts/02_transfermarkt.py
python scripts/03_clean.py
python scripts/04_analyse.py
```
 
To generate the HTML output:
 
```bash
jupyter nbconvert --to html blog.ipynb --output docs/index.html
```

## Features
 
- Collects Premier League player statistics from Understat via the soccerdata library
- Loads and processes Transfermarkt player market valuations from a publicly available dataset
- Merges two datasets across three seasons with name normalisation and loan player handling
- Runs OLS regression to identify significant drivers of player market value
- Produces six figures covering summary statistics, correlations, regression results, and squad level analysis
 
## Data Sources
 
- Player statistics: Understat.com via the soccerdata Python library (seasons 2022/23, 2023/24, 2024/25)
- Market values: Transfermarkt dataset by David Cariboo from https://github.com/dcaribou/transfermarkt-datasets
- League standings: Manually sourced from the Official Premier League website