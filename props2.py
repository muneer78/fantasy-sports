import re
import pandas as pd
from icecream import ic
from pandas_log import enable
from skimpy import skim

# Load data
dfsched = pd.read_excel("roster-resource-download.xlsx", usecols=[0, 1, 2])
dfprops = pd.read_csv("fangraphs-leaderboards.csv")

# Clean and process dfprops
dfprops['K/GS'] = (dfprops['SO'] / dfprops['GS']).round(2)
dfprops['BB/GS'] = (dfprops['BB'] / dfprops['GS']).round(2)
dfprops['IP/G'] = (dfprops['IP'] / dfprops['GS']).round(0)
dfprops = dfprops.loc[
    (dfprops['GS'] > 1) &
    (dfprops['IP/G'] >= 5) &
    (dfprops['IP/G'] < 8) &
    (dfprops['K/GS'] <= 9) &
    (dfprops['BB/GS'] <= 6)
]

# Clean and process dfsched
dfsched.rename(columns={dfsched.columns[2]: "Name"}, inplace=True)
dfsched = dfsched.fillna(0)
dfsched['Name'] = dfsched['Name'].apply(delete_first_line).apply(remove_text)
opposing_teams = dfsched.iloc[:, 1].str.split("\n").str[0]
dfsched["OpposingTeam"] = opposing_teams
dfsched["OpposingTeam"] = dfsched["OpposingTeam"].str.replace("@ ", "")

# Load and process opponent data
dfopponents = pd.read_csv("fangraphs-leaderboards (1).csv", usecols=["Team", "K%", "BB%"])
dfopponents.sort_values("K%", ascending=False, ignore_index=True, inplace=True)
dfopponents["KRank"] = range(1, len(dfopponents) + 1)
dfopponents.sort_values("BB%", ascending=True, ignore_index=True, inplace=True)
dfopponents["BBRank"] = range(1, len(dfopponents) + 1)

# Merge data
merged_dfsched = pd.merge(dfsched, dfopponents[["Team", "KRank", "BBRank"]], on="Team", how="left")

# Filter and sort dataframes
dfsortedBB = dfprops.sort_values("BB%+", ascending=True)
dfbbtop25 = dfsortedBB.head(25).fillna(0)
dfsortedK = dfprops.sort_values("K%+", ascending=False)
dfktop25 = dfsortedK.head(25).fillna(0)

# Extract matching data
matching_dfbbtop25 = get_matching_data(merged_dfsched, dfbbtop25, "BBRank", 10)
matching_dfktop25 = get_matching_data(merged_dfsched, dfktop25, "KRank", 10)

# More similar processing for another day's data
dfsched2 = pd.read_excel("roster-resource-download.xlsx", usecols=[0, 1])
dfprops2 = pd.read_csv("fangraphs-leaderboards.csv")

# Reuse the same functions for cleaning and processing
dfsched2 = clean_and_process_df(dfsched2, dfprops2)
dfopponents2 = clean_and_process_opponents("fangraphs-leaderboards (1).csv")

# Merge and extract matching data for the second day
matching_dfbbtop252 = get_matching_data(dfsched2, dfprops2, dfopponents2, dfbbtop25, "BBRank", 10)
matching_dfktop252 = get_matching_data(dfsched2, dfprops2, dfopponents2, dfktop25, "KRank", 10)

# Combine all matching data
list_of_dfs = [matching_dfktop252, matching_dfbbtop252, matching_dfktop25, matching_dfbbtop25]

# Write data to file
titles = [
    "Pitcher High Strikeout Props Today",
    "Pitcher Low BB Props Today",
    "Pitcher High Strikeout Props Tomorrow",
    "Pitcher Low BB Props Tomorrow",
]

with open("props.csv", "w+", encoding="utf8") as f:
    for i, df in enumerate(list_of_dfs):
        if not df.empty:
            f.write(titles[i] + "\n")
            df.round(2).to_csv(f, index=False)
            f.write("\n")
