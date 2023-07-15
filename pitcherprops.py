import re
import pandas as pd
"""
Provides some arithmetic functions and ability to use regex
"""

dfsched = pd.read_excel("roster-resource-download.xlsx", usecols=[0, 1])
dfprops = pd.read_csv("FanGraphs Leaderboard.csv")

dfsched.rename(columns={dfsched.columns[1]: "Name"}, inplace=True)
dfsched = dfsched.fillna(0)

dfopponents = pd.read_csv(
    "FanGraphs Leaderboard(10).csv", usecols=["Team", "K%", "BB%"]
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
Deletes first line in cell from roster resourec file
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

dfsched = pd.merge(
    dfsched, dfopponents[["Team", "KRank", "BBRank"]], on="Team", how="left"
)

dfsortedBB = dfprops.sort_values("BB%+", ascending=True)
dfbbtop25 = dfsortedBB.head(25).fillna(0)

dfsortedK = dfprops.sort_values("K%+", ascending=False)
dfktop25 = dfsortedK.head(25).fillna(0)

matching_dfbbtop25 = dfsched[dfsched["Name"].isin(dfbbtop25["Name"])]
matching_dfktop25 = dfsched[dfsched["Name"].isin(dfktop25["Name"])]

matching_dfbbtop25 = dfsched[
    (dfsched["Name"].isin(dfbbtop25["Name"])) & ((dfsched["BBRank"] <= 10))
]
matching_dfktop25 = dfsched[
    (dfsched["Name"].isin(dfktop25["Name"])) & ((dfsched["KRank"] <= 10))
]

matching_dfktop25 = pd.merge(
    matching_dfktop25, dfktop25[["Name", "K%+", "BB%+"]], on="Name", how="left"
)
matching_dfbbtop25 = pd.merge(
    matching_dfbbtop25, dfbbtop25[["Name", "K%+", "BB%+"]], on="Name", how="left"
)

matching_dfktop25 = matching_dfktop25.sort_values(by="K%+", ascending=False)
matching_dfbbtop25 = matching_dfbbtop25.sort_values(by="BB%+", ascending=True)

# print("Low walk props to explore:")
# print(matching_dfbbtop25)
# print(" ")
# print("High strikeout props to explore:")
# print(matching_dfktop25)

list_of_dfs = [matching_dfktop25, matching_dfbbtop25]

titles = [
    "Pitcher High Strikeout Props",
    "Pitcher Low BB Props",
]

with open("props.csv", "w+", encoding="utf8") as f:
    for i, df in enumerate(list_of_dfs):
        f.write(titles[i] + "\n")  # Write the title
        df.to_csv(f, index=False)
        f.write("\n")
