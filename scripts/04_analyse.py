# Before running this script, create the output folder by running the following in wsl terminal: mkdir -p figures

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

# Load clean datasets

players = pd.read_csv("data/clean/players.csv")
squads  = pd.read_csv("data/clean/squads.csv")

print("Players: " + str(players.shape))
print("Squads : " + str(squads.shape))

# Set consistent high contrast colour palette across all figures

SEASON_COLOURS = {
    "2022/2023": "#1b9e77",
    "2023/2024": "#d95f02",
    "2024/2025": "#7570b3",
}

# Figure 1 - Summary statistics table
# Shows the distribution of transfer values and statistics across all Premier League players in the dataset

summary_cols = ["market_value_m", "age", "minutes", "npxg_p90", "xa_p90", "kp_p90"]
summary = players[summary_cols].describe().round(2)
summary.index = ["Count", "Mean", "Std Dev", "Min", "25th Pct", "Median", "75th Pct", "Max"]
summary.columns = ["Market Value (€m)", "Age", "Minutes", "npxG p90", "xA p90", "Key Passes p90"]

fig, ax = plt.subplots(figsize=(10, 4))
ax.axis("off")

table = ax.table(
    cellText=summary.values,
    rowLabels=summary.index,
    colLabels=summary.columns,
    cellLoc="center",
    loc="center",
)

table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 1.6)

ax.set_title("Summary Statistics: Premier League Players (2022/23 - 2024/25)", fontweight="bold", pad=20, fontsize=13)

plt.tight_layout()
plt.savefig("figures/fig1_summary_statistics.png", bbox_inches="tight")
plt.close()

# Figure 2 - Correlation heatmap
# Shows how performance metrics correlate with market value

corr_cols = ["market_value_m", "age", "minutes", "npxg_p90", "xa_p90", "kp_p90", "goals_p90", "assists_p90"]
corr_labels = ["Market Value", "Age", "Minutes", "npxG p90", "xA p90", "Key Passes p90", "Goals p90", "Assists p90"]

corr_matrix = players[corr_cols].corr().round(2)

fig, ax = plt.subplots(figsize=(10, 8))

im = ax.imshow(corr_matrix.values, cmap="RdYlGn", vmin=-1, vmax=1)
plt.colorbar(im, ax=ax)

ax.set_xticks(range(len(corr_labels)))
ax.set_yticks(range(len(corr_labels)))
ax.set_xticklabels(corr_labels, rotation=45, ha="right", fontsize=9)
ax.set_yticklabels(corr_labels, fontsize=9)

for i in range(len(corr_cols)):
    for j in range(len(corr_cols)):
        val = corr_matrix.values[i, j]
        colour = "white" if abs(val) > 0.6 else "black"
        ax.text(j, i, str(val), ha="center", va="center", fontsize=8, color=colour)

ax.set_title("Correlation Matrix: Market Value and Player Performance Metrics", fontweight="bold")

plt.tight_layout()
plt.savefig("figures/fig2_correlation_heatmap.png", bbox_inches="tight")
plt.close()

# OLS Regression - what drives player market value?
# Dependent variable: log(market_value_m)
# Independent variables: npxg_p90, xa_p90, kp_p90, minutes, age, age squared, position dummies (Forward as reference category)
# Goalkeepers excluded as their value drivers differ from outfield players
# Age^2 captures the peak then decline of player value

outfield = players[players["position_clean"] != "Goalkeeper"].copy()
outfield = outfield[outfield["age"].notna()].copy()

print("\nOutfield players used in regression: " + str(len(outfield)))

# Create position dummies

dummies = pd.get_dummies(outfield["position_clean"], drop_first=False)
dummies = dummies.drop(columns="Forward")
dummies.columns = ["Defender", "Midfielder"]
outfield = pd.concat([outfield, dummies], axis=1)

formula = "log_market_value ~ npxg_p90 + xa_p90 + minutes + age + I(age**2) + Defender + Midfielder"

player_model = smf.ols(formula=formula, data=outfield).fit()

print("\nOLS Regression: What drives player market value?")
print(player_model.summary())

open("figures/player_regression_summary.txt", "w").write(str(player_model.summary()))

# Calculate peak age from regression coefficients
# peak = -coef(age) / (2 * coef(age squared))

age_coef = player_model.params["age"]
age_sq_coef = player_model.params["I(age ** 2)"]
peak_age = -age_coef / (2 * age_sq_coef)

print("Peak age from regression: " + str(round(peak_age, 1)))

# Figure 3 - Coefficient plot from player regression
# Shows which performance metrics significantly drive market value

coef_df = pd.DataFrame({"coef": player_model.params, "pvalue": player_model.pvalues}).reset_index()
coef_df = coef_df[coef_df["index"] != "Intercept"].copy()

label_map = {
    "npxg_p90": "npxG per 90",
    "xa_p90": "xA per 90",
    "minutes": "Minutes Played",
    "age": "Age",
    "I(age ** 2)": "Age²",
}

coef_df["label"] = coef_df["index"].map(label_map).fillna(coef_df["index"])

fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(coef_df["label"], coef_df["coef"])
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Coefficient")
ax.set_title("OLS Regression Coefficients", fontweight="bold")

plt.tight_layout()
plt.savefig("figures/fig3_coefficients.png", bbox_inches="tight")
plt.close()

# Figure 4 - Most over and undervalued players
# Players with the largest positive residuals are undervalued by the model relative to their on pitch performance and vice versa for negative residuals

outfield["predicted"] = player_model.fittedvalues
outfield["residual"] = outfield["log_market_value"] - outfield["predicted"]

# Average residual per player across seasons 

avg_residuals = (outfield.groupby("player")["residual"].mean().reset_index().rename(columns={"residual": "avg_residual"}))

top10_under = avg_residuals.sort_values("avg_residual", ascending=False).head(10).sort_values("avg_residual")
top10_over = avg_residuals.sort_values("avg_residual", ascending=True).head(10).sort_values("avg_residual", ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].barh(top10_under["player"], top10_under["avg_residual"], color="#009E73", edgecolor="white")
axes[0].axvline(0, color="black", linewidth=0.8)
axes[0].set_xlabel("Average Residual (log scale)")
axes[0].set_title("Model Underpredicts Value\n(Market pays more than stats suggest)", fontweight="bold")

axes[1].barh(top10_over["player"], top10_over["avg_residual"], color="#D55E00", edgecolor="white")
axes[1].axvline(0, color="black", linewidth=0.8)
axes[1].set_xlabel("Average Residual (log scale)")
axes[1].set_title("Model Overpredicts Value\n(Market pays less than stats suggest)", fontweight="bold")

fig.suptitle("Transfer Market Mispricing: Where the Model Diverges from the Market (2022/23 - 2024/25)", fontweight="bold", fontsize=13)

plt.tight_layout()
plt.savefig("figures/fig4_over_undervalued.png", bbox_inches="tight")
plt.close()

# Figure 5 - Squad value rank vs league position across all 3 seasons
# Shows whether the most expensive squads finish higher in the league table than cheaper squads with a perfect correlation line

squads["points_rank"] = squads.groupby("season")["points"].rank(ascending=False).astype(int)
squads["value_rank"]  = squads.groupby("season")["squad_value_m"].rank(ascending=False).astype(int)

fig, ax = plt.subplots(figsize=(10, 7))

for season, grp in squads.groupby("season"):
    ax.scatter(grp["value_rank"], grp["points_rank"], color=SEASON_COLOURS[season], s=60, alpha=0.8, label=season)

    # Annotate club names next to league position vs value rank
    
    for _, row in grp.iterrows():
        ax.annotate(row["club_std"], xy=(row["value_rank"], row["points_rank"]), xytext=(3, 3), textcoords="offset points", fontsize=6, alpha=0.8)

ax.plot([1, 20], [1, 20], color="black", linewidth=1, linestyle="--", label="Perfect correlation")
ax.set_xlabel("Squad Value Rank (1 = most expensive)")
ax.set_ylabel("League Position (1 = champions)")
ax.set_title("Does Money Buy Success?\nSquad Value Rank vs League Position (2022/23 - 2024/25)", fontweight="bold")
ax.legend()

plt.tight_layout()
plt.savefig("figures/fig5_rank_comparison.png", bbox_inches="tight")
plt.close()

# OLS Regression - does squad value predict league points?
# Dependent variable: points
# Independent variables: log(squad_value_m), avg_age
# Uses all 60 club-season observations across three seasons

squad_model = smf.ols("points ~ log_squad_value + avg_age", data=squads).fit()

print("\nOLS Regression: Does squad value predict league points?")
print(squad_model.summary())

open("figures/squad_regression_summary.txt", "w").write(str(squad_model.summary()))

# Figure 6 - Squad regression with fitted line
# Shows the relationship between log squad value and points with the OLS fitted line and R squared value

fig, ax = plt.subplots(figsize=(9, 6))

for season, grp in squads.groupby("season"):
    ax.scatter(grp["log_squad_value"], grp["points"], color=SEASON_COLOURS[season], alpha=0.8, s=60, label=season)

x_vals = pd.Series([squads["log_squad_value"].min(), squads["log_squad_value"].max()])
y_vals = squad_model.params["Intercept"] + squad_model.params["log_squad_value"] * x_vals
ax.plot(x_vals, y_vals, color="black", linewidth=2, label="OLS fit (R² = " + str(round(squad_model.rsquared, 2)) + ")")

ax.set_xlim(squads["log_squad_value"].min() - 0.1, squads["log_squad_value"].max() + 0.1)
ax.set_ylim(0,100)

ax.set_xlabel("Log Squad Value")
ax.set_ylabel("Final League Points")
ax.set_title("Squad Value vs League Points: OLS Regression\n(2022/23 - 2024/25)", fontweight="bold")
ax.legend()

plt.tight_layout()
plt.savefig("figures/fig6_squad_regression.png", bbox_inches="tight")
plt.close()