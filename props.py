"""
Provides some arithmetic functions and ability to use regex
"""

import re
import pandas as pd

dfsched = pd.read_excel("roster-resource-download.xlsx", usecols=[0, 1, 2])
dfprops = pd.read_csv("FanGraphs Leaderboard.csv")

dfprops['K/GS'] = dfprops['SO'] / dfprops['GS']
dfprops ['K/GS' ] = dfprops['K/GS'].round(2)
dfprops['BB/GS'] = dfprops['BB'] / dfprops['GS']
dfprops['BB/GS'] = dfprops['BB/GS'].round(2)
dfprops['IP/G'] = dfprops['IP'] / dfprops['GS']
dfprops['IP/G'] = dfprops['IP/G'].round(0)

# Filter rows where GS > 1
dfprops = dfprops.loc[(dfprops['GS'] > 1) & (dfprops['IP/G'] > 5)]

dfsched.rename(columns={dfsched.columns[2]: "Name"}, inplace=True)
dfsched = dfsched.fillna(0)

# Delete the second column from dfsched
dfsched = dfsched.drop(dfsched.columns[1], axis=1)

dfopponents = pd.read_csv(
    "FanGraphs Leaderboard (1).csv", usecols=["Team", "K%", "BB%"]
)

dfopponents["K%"] = dfopponents["K%"].str.rstrip("%").astype(float)
dfopponents["BB%"] = dfopponents["BB%"].str.rstrip("%").astype(float)

dfopponents.sort_values("K%", ascending=False, ignore_index=True, inplace=True)

# Add a new column called "KRank"
dfopponents["KRank"] = range(1, len(dfopponents) + 1)


dfopponents.sort_values("BB%", ascending=True, ignore_index=True, inplace=True)
dfopponents["BBRank"] = range(1, len(dfopponents) + 1)

dfsched["Name"] = dfsched["Name"].str.strip()
opposing_teams = dfsched.iloc[:, 1].str.split("\n").str[0]
dfsched["OpposingTeam"] = opposing_teams
dfsched["OpposingTeam"] = dfsched["OpposingTeam"].str.replace("@ ", "")

"""
Deletes first line in cell from roster resource file
"""
def delete_first_line(cell_value):
    lines = cell_value.split("\n")
    if len(lines) > 1:
        lines.pop(0)
    return "\n".join(lines)

"""
Applies delete_first_line function
"""
dfsched = dfsched.applymap(delete_first_line)

"""
Remove the R or L from after pitcher name
"""
def remove_text(cell_value):
    pattern = r"\s*\(R\)|\s*\(L\)"
    return re.sub(pattern, "", cell_value)


dfsched = dfsched.applymap(remove_text)

merged_dfsched = pd.merge(dfsched, dfopponents[["Team", "KRank", "BBRank"]], on="Team", how="left")

dfsortedBB = dfprops.sort_values("BB%+", ascending=True)
dfbbtop25 = dfsortedBB.head(25).fillna(0)

dfsortedK = dfprops.sort_values("K%+", ascending=False)
dfktop25 = dfsortedK.head(25).fillna(0)

matching_dfbbtop25 = merged_dfsched[merged_dfsched["Name"].isin(dfbbtop25["Name"])]
matching_dfktop25 = merged_dfsched[merged_dfsched["Name"].isin(dfktop25["Name"])]

matching_dfbbtop25 = merged_dfsched[
    (merged_dfsched["Name"].isin(dfbbtop25["Name"])) & ((merged_dfsched["BBRank"] <= 10))
]
matching_dfktop25 = merged_dfsched[
    (merged_dfsched["Name"].isin(dfktop25["Name"])) & ((merged_dfsched["KRank"] <= 10))
]

matching_dfktop25 = pd.merge(
    matching_dfktop25, dfktop25[["Name", "K%+", "BB%+", "xFIP", "K/GS"]], on="Name", how="left"
)
matching_dfbbtop25 = pd.merge(
    matching_dfbbtop25, dfbbtop25[["Name", "K%+", "BB%+", "xFIP", "BB/GS"]], on="Name", how="left"
)

matching_dfktop25 = matching_dfktop25.sort_values(by="K%+", ascending=False)
matching_dfbbtop25 = matching_dfbbtop25.sort_values(by="BB%+", ascending=True)

'''
Code to show today's plays
'''''

dfsched2 = pd.read_excel("roster-resource-download.xlsx", usecols=[0, 1])
dfprops2 = pd.read_csv("FanGraphs Leaderboard.csv")

dfprops2['K/GS'] = dfprops2['SO'] / dfprops2['GS']
dfprops2 ['K/GS' ] = dfprops2['K/GS'].round(2)
dfprops2['BB/GS'] = dfprops2['BB'] / dfprops2['GS']
dfprops2['BB/GS'] = dfprops2['BB/GS'].round(2)
dfprops2['IP/G'] = dfprops2['IP'] / dfprops2['GS']
dfprops2['IP/G'] = dfprops2['IP/G'].round(0)

# Filter rows where GS > 1
dfprops2 = dfprops2.loc[(dfprops2['GS'] > 1) & (dfprops2['IP/G'] > 5)]

dfsched2.rename(columns={dfsched2.columns[1]: "Name"}, inplace=True)
dfsched2 = dfsched2.fillna(0)

dfopponents2 = pd.read_csv(
    "FanGraphs Leaderboard (1).csv", usecols=["Team", "K%", "BB%"]
)

dfopponents2["K%"] = dfopponents2["K%"].str.rstrip("%").astype(float)
dfopponents2["BB%"] = dfopponents2["BB%"].str.rstrip("%").astype(float)

dfopponents2.sort_values("K%", ascending=False, ignore_index=True, inplace=True)


# Add a new column called "KRank"
dfopponents2["KRank"] = range(1, len(dfopponents) + 1)


dfopponents2.sort_values("BB%", ascending=True, ignore_index=True, inplace=True)
dfopponents2["BBRank"] = range(1, len(dfopponents2) + 1)

dfsched2["Name"] = dfsched2["Name"].str.strip()
opposing_teams2 = dfsched2.iloc[:, 1].str.split("\n").str[0]
dfsched2["OpposingTeam"] = opposing_teams2
dfsched2["OpposingTeam"] = dfsched2["OpposingTeam"].str.replace("@ ", "")

"""
Deletes first line in cell from roster resource file
"""
def delete_first_line(cell_value):
    lines = cell_value.split("\n")
    if len(lines) > 1:
        lines.pop(0)
    return "\n".join(lines)

"""
Applies delete_first_line function
"""
dfsched2 = dfsched2.applymap(delete_first_line)

"""
Remove the R or L from after pitcher name
"""
def remove_text(cell_value):
    pattern = r"\s*\(R\)|\s*\(L\)"
    return re.sub(pattern, "", cell_value)


dfsched2 = dfsched2.applymap(remove_text)

# Generate dfopponents again
dfopponents2 = pd.read_csv("FanGraphs Leaderboard (1).csv", usecols=["Team", "K%", "BB%"])

# Update columns in dfopponents2
dfopponents2["K%"] = dfopponents2["K%"].str.rstrip("%").astype(float)
dfopponents2["BB%"] = dfopponents2["BB%"].str.rstrip("%").astype(float)

# Sort and add ranking columns
dfopponents2.sort_values("K%", ascending=False, ignore_index=True, inplace=True)
dfopponents2["KRank"] = range(1, len(dfopponents2) + 1)
dfopponents2.sort_values("BB%", ascending=True, ignore_index=True, inplace=True)
dfopponents2["BBRank"] = range(1, len(dfopponents2) + 1)

# Update merged_merged_dfsched2 with opponent data again
dfsched2 = pd.merge(dfsched2, dfopponents2[["Team", "KRank", "BBRank"]], on="Team", how="left")

dfsortedBB2 = dfprops2.sort_values("BB%+", ascending=True)
dfbbtop252 = dfsortedBB2.head(25).fillna(0)

dfsortedK2 = dfprops2.sort_values("K%+", ascending=False)
dfktop252 = dfsortedK2.head(25).fillna(0)

matching_dfbbtop252 = dfsched2[dfsched2["Name"].isin(dfbbtop252["Name"])]
matching_dfktop252 = dfsched2[dfsched2["Name"].isin(dfktop252["Name"])]

matching_dfbbtop252 = dfsched2[
    (dfsched2["Name"].isin(dfbbtop252["Name"])) & ((dfsched2["BBRank"] <= 10))
]
matching_dfktop252 = dfsched2[
    (dfsched2["Name"].isin(dfktop252["Name"])) & ((dfsched2["KRank"] <= 10))
]

matching_dfktop252 = pd.merge(
    matching_dfktop252, dfktop252[["Name", "K%+", "BB%+", "xFIP", "K/GS"]], on="Name", how="left"
)
matching_dfbbtop252 = pd.merge(
    matching_dfbbtop252, dfbbtop252[["Name", "K%+", "BB%+", "xFIP", "BB/GS"]], on="Name", how="left"
)

matching_dfktop252 = matching_dfktop252.sort_values(by="K%+", ascending=False)
matching_dfbbtop252 = matching_dfbbtop252.sort_values(by="BB%+", ascending=True)

list_of_dfs = [matching_dfktop252, matching_dfbbtop252, matching_dfktop25, matching_dfbbtop25]

titles = [
    "Pitcher High Strikeout Props Today",
    "Pitcher Low BB Props Today",
    "Pitcher High Strikeout Props Tomorrow",
    "Pitcher Low BB Props Tomorrow",
]

with open("props.csv", "w+", encoding="utf8") as f:
    for i, df in enumerate(list_of_dfs):
        if not df.empty:  # Check if the dataframe is not empty
            f.write(titles[i] + "\n")  # Write the title
            df.to_csv(f, index=False)
            f.write("\n")